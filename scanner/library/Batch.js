class Batch {
    constructor (func,batchSize = 500) {
        this.func = func
        this.batchSize = batchSize
    }
    __queued = []
    async add(item) {
        this.__queued.push(item)
        
        // We're not checking for concurrency/locking
        // because that will impact performance too much
        // It is good to prevent wastage that
        // these three lines run at once
        // And other instances don't override
        // But isn't that important, so we'll leave that alone
        if (this.__queued.length >= this.batchSize) {
            await this.process()
        }
    }
    async process() {
        const batch = [...this.__queued]
        this.__queued = []
        await this.func(batch)
    }
}
exports.Batch = Batch