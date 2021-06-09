const { TokenScanner } = require("./library/TokenScanner");
const { DB } = require('./library/DB');
const { sleep } = require("./library/Thread");

while (true) {
    console.log("Starting/Restarting scanner")
    const db = new DB("tokens")
    const scanner = await (new TokenScanner({
        startFrom: -10,
        threading: 11,
        chunks: 50,
        providers: [0,1,2,4],
        db
    })).setup();
    
    await (() => (new Promise((resolve) => {
        scanner.start()
        .catch(error => {
            console.error(error)
            console.log(`Error in main script`)
        })
        .finally(() => resolve())
    })) )()
    await sleep(5000)
}