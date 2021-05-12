import AwesomeDebouncePromise from 'awesome-debounce-promise';
import { createRef, useState } from "react";

import InputBase from '@material-ui/core/InputBase'

import SearchIcon from '@material-ui/icons/Search';

import ResultsPopover from './ResultsPopover';
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
    const searchRef = createRef();
    const classes = searchStyles();

    const [resultsOpen,setResultsOpen] = useState(false);
    const [resultsWidth,setResultsWidth] = useState(null);
    const [anchorEl,setAnchorEl] = useState(null);
    
    const handleResultsOpen = (open,event) => {
        setResultsOpen(open);
        if (open) {
            setResultsWidth(getComputedStyle(searchRef.current).width);
            setAnchorEl(searchRef.current);
        }
    }

    return (
        <div className={classes.searchWrapper} >
            <div className={classes.search} ref={searchRef}>
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
                onFocus={handleResultsOpen.bind(null,true)}
                onBlur={handleResultsOpen.bind(null,false)}
                placeholder="Search token"
                classes={{
                    root: classes.inputRoot,
                    input: classes.inputInput,
                }}
                inputProps={{ 'aria-label': 'search' }}
                />
            </div>
            <ResultsPopover
            open={resultsOpen}
            anchorEl={anchorEl}
            width={resultsWidth}
            />
        </div>
    )
}
export default Search;