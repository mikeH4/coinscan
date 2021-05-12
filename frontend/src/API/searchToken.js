import AwesomeDebouncePromise from "awesome-debounce-promise";

const search = AwesomeDebouncePromise(
    async search => await (await fetch(`https://tokenfomo.io`)).body,
    300
);

JSON.parse(temp1.innerText).props.pageProps.tokens.filter(({chainId}) => chainId == "BSC");

export default search;