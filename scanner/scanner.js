const { TokenScanner } = require("./library/TokenScanner");
const { DB } = require('./library/DB');

(async () => {
    while (true) {
        console.log("Starting/Restarting scanner")
        const db = new DB("tokens")
        const scanner = await (new TokenScanner({
            startFrom: -10,
            threading: 15,
            chunks: 10,
            providers: [0,1,2,4],
            db
        })).setup();

        try {
            await Promise.all([scanner.pull(),scanner.process()])
        } catch (error) {
            console.error(error)
        }
        console.log("All ended")
    }
})()