import { createRef, useState } from "react";

import InputBase from '@material-ui/core/InputBase'

import SearchIcon from '@material-ui/icons/Search';

import ResultsPopover from './ResultsPopover';
import searchStyles from './styles';


const Search = () => {
    const searchRef = createRef();
    const classes = searchStyles();

    const [items,setItems] = useState([]);
    const [loading,setLoading] = useState(false);

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
                    const result = {};
                    try {
                        setLoading(false);
                        setItems(result.found || []);
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
            results={items}
            loading={loading}
            />
        </div>
    )
}
export default Search;