import React, { useState } from 'react';
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';

import IconButton from '@material-ui/core/IconButton';
import MenuIcon from '@material-ui/icons/Menu';

import Search from "../Search/Search";
import styles from "./styles";

function Header() {
    const classes = styles();
    const [items,setItems] = useState([]);
    const [loading,setLoading] = useState(false);

    return (
        <div className={classes.root}>
            <AppBar position="static">
                <Toolbar className={classes.toolbar}>
                    <IconButton
                    className={classes.menuButton}
                    color="inherit"
                    aria-label="menu"
                    >
                        <MenuIcon/>
                    </IconButton>
                    <Typography variant="h6" className={classes.title}>
                        Coin    Scan
                    </Typography>
                    <Search
                    setItems={setItems}
                    setLoading={setLoading}
                    />
                    <Button color="inherit">Connect Wallet</Button>
                    </Toolbar>
            </AppBar>
        </div>
    );
}

export default Header;