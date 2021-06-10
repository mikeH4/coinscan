class DelayedBatcher {
    // All times are in secs
    constructor (func, delay = 5) {
        this.func = func
        this.delay = delay
    }
    __store = {}
    add (item) {
        this.__slot().push(item)
    }
    collect () {
        const now = DelayedBatcher.__now()-this.delay
        const forCollection = []
        for (const [timestamp,items] of Object.entries(this.__store)) {
            if (now < timestamp) {
                break
            }
            forCollection.push(...items)
        }
        return forCollection
    }
    __slot () {
        this.__store[DelayedBatcher.__now()] = this.__store[DelayedBatcher.__now()] || []
        return this.__store[DelayedBatcher.__now()]
    }
    static __now() {
        return Math.ceil(Date.now()/1000)
    }
}
exports.DelayedBatcher = DelayedBatcher
class KeyedDelayedBatcher extends DelayedBatcher {
    __keyItemStore = {}
    add (key,item) {
        if (!this.__keyItemStore[key]) {
            super.add(key)
        }
        this.__keyItemStore[key] = item
    }
    collect () {
        const now = DelayedBatcher.__now()-this.delay
        const forCollection = []
        for (const [timestamp,keys] of Object.entries(this.__store)) {
            if (now < timestamp) {
                break
            }
            for (const key in keys) {
                const item = this.__keyItemStore[key]
                // We're doing this because we don't want to miss an object
                // In case of concurrrent threads
                delete this.__keyItemStore[key]
                forCollection.push(item)
            }
        }
        return forCollection
    }
    // Alias
    update (...args) {
        this.add(...args)
    }
}
exports.KeyedDelayedBatcher = KeyedDelayedBatcher