const { Pool } = require('pg')
const settings = require("../settings.json")

exports.DB = class {
    constructor (db) {
        this.__db = db
        const args = {
            host: "localhost",
            database: db
        }

        if (settings.sandbox != true) {
            args.user = "coinscan"
            args.password = "root"
        }

        this.__pool = new Pool (args)
        this.__pool.on("error",(error, client) => {
            console.error(error)
            console.log("Error with connection: Retrying")
            this.__pool = new Pool(args)
        })
        for (const method of ["insert","getall","get","query"]) {
            this[method] = async (...args) => {
                const client = await this.client()
                try {
                    return (await client[method](...args));
                } catch (error) {
                    console.error(error)
                } finally {
                    client.release()
                }
            }
        }
    }

    async close () {
        await this.__pool.end()
    }
    
    async client() {
        return new Client(await this.__pool.connect())
    }

    async block (func) {
        const client = await this.client()
        await func(client)
        await client.release()
    }

    async commitBlock (func) {
        const client = await this.client()
        await client.commitBlock(() => {
            func(client)
        })
        await client.release()
    }

    placeholder = Client.placeholder
}

class Client {
    static clientsCreated = 0
    static active = {}
    constructor (client) {
        this.id = Client.clientsCreated
        // To increment id if another thread wins race
        while (Client.active[this.id]) {
            Client.clientsCreated += 1
            this.id = Client.clientsCreated
        }
        Client.clientsCreated += 1
        Client.active[this.id] = true
        console.log(`Client created:`,this.id)
        console.log("Active clients:",Object.keys(Client.active).length)
        this.__creationTimer = setTimeout(() => {
            console.log("Client has been active for more than 6 secs! =>",this.id)
        },6000)
        this.__minuteTimer = setTimeout(() => {
            console.log("Client has been active for more than a minute! =>",this.id)
        },60000)
        
        this.client = client
        this.placeholder = Client.placeholder
    }

    // Query Helpers
    async insert (table,data,{
        commit=true,
        replace_on=[],
        dont_update=[],
        ignore=false
    } = {}) {
        const cols = Object.keys(data)
        const colstr = cols.join(",")
        const placeholder = this.placeholder(cols.length)
        let sql = `INSERT INTO ${table} (${colstr}) VALUES (${placeholder})`
        if (ignore) {
            sql += ` ON CONFLICT DO NOTHING`
        }
        else if (replace_on.length >= 1) {
            for (const replace_col of replace_on) {
                if (!replace_on.includes(replace_col)) {
                    throw new Error("replace_on must be one of columns inserted")
                }
            }
            const update_str = (
                cols
                .filter(key => !replace_on.includes(key) && !dont_update.includes(key))
                .map(key => `${key} = excluded.${key}`)
            )
            sql += ` ON CONFLICT (${replace_on.join(", ")}) DO UPDATE SET ${update_str}`
        }
        sql += ";"
        await this.query(sql,Object.values(data),{commit})
    }
    async getall (query,params = []) {
        const res = await this.client.query(query,params)
        return res.rows
    }
    async get (query,params = []) {
        rows = this.getall(query,params)
        return query[0] || null;
    }
    async query (query,params = [],{commit=true} = {}) {
        if (!commit) {
            await this.client.query(query, params);
            return
        }
        await this.commitBlock(async () => {
            await this.client.query(query, params);
        })
    }
    // Low Level
    async begin () {
        await this.client.query("BEGIN;");
    }
    async commit () {
        await this.client.query("COMMIT;");
    }
    async rollback () {
        await this.client.query("ROLLBACK;");
    }
    async release () {
        delete Client.active[this.id]
        clearTimeout(this.__creationTimer)
        clearTimeout(this.__minuteTimer)
        return this.client.release()
    }
    // Wrappers
    async commitBlock(func) {
        await this.begin()
        try {
            await func(this)
            await this.commit()                
        } catch (error) {
            console.error(error)
            this.rollback()
        }
    }
    // Utils
    static placeholder (length) {
        return (Array(length).fill().map((_, i) => `$${i+1}`)).join(", ")
    }
}