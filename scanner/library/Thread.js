const sleep = (time = 1000) => new Promise(r => setTimeout(r, time));
exports.sleep = sleep

const timer = name => {
    const _start = Date.now()
    return () => {
        console.log(`${name} took ${Date.now() - _start} milliseconds`)
    }
}
exports.timer = timer

class Threads {
    static __threadsCreated = 0
    __active = {}
    __concurrent

    constructor (concurrent = 5,name = null) {
        this.name = !name ? `Threads ${Threads.__threadsCreated}` : name
        this.__concurrent = concurrent
        Threads.__threadsCreated += 1
    }
    async freed () {
        while (!this.isFree()) {
            await sleep(1);
        }
    }
    async completed () {
        while (!this.isComplete()) {
            await sleep(1);
        }
    }
    isFree () {
        return this.ongoing() < this.__concurrent
    }
    isComplete () {
        return this.ongoing() <= 0
    }
    ongoing () {
        return Object.keys(this.__active).length
    }
    checkout (id) {
        if (typeof this.__active[id] !== "undefined") {
            throw new Error("Duplicate thread ID:",this.__active[id])
        }
        this.__active[id] = null;
        console.log("Checked out thread:",id,"=>",this.name)
        return new SingleThread(id,this)
    }
    release (id) {
        console.log("Released thread:",id,"=>",this.name)
        delete this.__active[id]
    }
}
exports.Threads = Threads

class SingleThread {
    constructor (id,fromThreads) {
        this.id = id
        this.fromThreads = fromThreads
        this.provider = fromThreads.provider
    }
    release () {
        this.fromThreads.release(this.id)
    }
}

class ThreadPool {
    __threads = []
    constructor (threads) {
        for (const thread of threads) {
            this.__threads.push(thread)
        }
    }
    async getAvailable () {
        while (true) {
            for (const thread of this.__threads) {
                if (thread.isFree()) {
                    return thread
                }
            }
            await sleep(1)
        }
    }
    async checkout (id) {
        return (await this.getAvailable()).checkout(id)
    }
    async completed () {
        for (const thread of this.__threads) {
            await thread.completed()
        }
    }
}


exports.ThreadPool = ThreadPool