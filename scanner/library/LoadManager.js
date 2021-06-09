class LoadManager {
    constructor(sourceFunc,cacheTime=20000) {
        this.__source = sourceFunc;
        this.__cacheTime = cacheTime;

        this.fetch = async () => {
            try {
                await this.__request();
                return this.__value;                    
            } catch (error) {
                console.log("Error in fetching with LoadManager",sourceFunc)
            }
        }
    }

    __value = null;

    __lastPulled = 0;
    __pendingPromise = null

    __shouldUpdate () {
        return (Date.now() - this.__lastPulled) > this.__cacheTime
    }

    __request() {
        if (this.__pendingPromise !== null) {
            return this.__pendingPromise
        }
        if (!this.__shouldUpdate()) {
            return new Promise((resolve) => resolve(this.__value))
        }
        const promise = new Promise(async (resolve,reject) => {
            this.__value = await this.__source()
            this.__lastPulled = Date.now()
            resolve(this.__value)
            this.__pendingPromise = null
        })
        this.__pendingPromise = promise
        return promise
    }
}
exports.LoadManager = LoadManager