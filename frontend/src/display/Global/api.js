import AwesomeDebouncePromise from 'awesome-debounce-promise';

export const all = AwesomeDebouncePromise(
    async () => await (await fetch('/latest/all',{
        method: "get",
        headers: {
            "Content-Type": "application/json"
        },
    })).json(),
    300
);
export const search = AwesomeDebouncePromise(
    async search => await (await fetch(`/token/search/${search}`,{
        method: "get",
        headers: {
            "Content-Type": "application/json"
        },
    })).json(),
    300
);