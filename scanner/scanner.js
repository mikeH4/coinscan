const { TokenScanner } = require("./lib/TokenScanner");
const { DB } = require('./lib/DB');
const { sleep } = require("./lib/Thread");

(async () => {
    while (true) {
        console.log("Starting/Restarting scanner")
        try {
            const db = new DB("tokens")
            const scanner = await (new TokenScanner({
                startFrom: -1,
                threading: 10,
                chunks: 50,
                providers: [0],
                db
            })).setup()
        
            await scanner.start()
        } catch (error) {
            console.error(error)
            console.log(`Error in main script`)
            await sleep(5000)
        }
    }
})()