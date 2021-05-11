import AwesomeDebouncePromise from 'awesome-debounce-promise';

import InputBase from '@material-ui/core/InputBase';
import SearchIcon from '@material-ui/icons/Search';

import searchStyles from './styles';

const searchAPI = async text => await (await fetch('/search',{
    method: "post",
    body: JSON.stringify({
        search: text,
        nonce: document.querySelector("input[name='nonce']").value,
        apikey: process.env.REACT_APP_SEARCH_API_KEY || ""
    }),
    headers: {
        "Content-Type": "application/json"
    },
})).json();
const debouncedSearch = AwesomeDebouncePromise(searchAPI,300);

const Search = ({setItems,setLoading}) => {
    const classes = searchStyles();
    return (
        <div className={classes.search}>
        <div className={classes.searchIcon}>
        <SearchIcon />
        </div>
        <InputBase
        fullWidth={true}
        color="primary"
        className={classes.input}
        onChange={async ({target}) => {
            if (target.value.trim() === "") {
                setItems([]);
                return;
            }
            setLoading(true);
            try {
                const result = await debouncedSearch(target.value);
                if (!result.status) {
                    window.location.reload();
                }
                setLoading(false);
                setItems(result.result);
            } catch (error) {
            }
        }}
        placeholder="Search token"
        classes={{
            root: classes.inputRoot,
            input: classes.inputInput,
        }}
        inputProps={{ 'aria-label': 'search' }}
        />
        </div>
    )
}
export default Search;