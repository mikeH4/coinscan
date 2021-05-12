import AwesomeDebouncePromise from "awesome-debounce-promise";

export const latest = AwesomeDebouncePromise(
    async () => await (await fetch('/latest/all',{
        method: "get",
        headers: {
            "Content-Type": "application/json"
        },
    })).json(),
    300
);