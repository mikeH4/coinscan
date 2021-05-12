import React, { useState } from 'react';
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import Typography from '@material-ui/core/Typography';

import IconButton from '@material-ui/core/IconButton';
import HomeIcon from '@material-ui/icons/Home';

import { Link } from 'react-router-dom';

import Search from "../Search/Search";
import styles from "./styles";

function Header() {
    const classes = styles();

    return (
        <div className={classes.root}>
            <AppBar position="static">
                <Toolbar className={classes.toolbar}>
                    <IconButton
                    component={Link}
                    to="/"
                    className={classes.menuButton}
                    color="inherit"
                    aria-label="menu"
                    >
                        <HomeIcon/>
                    </IconButton>
                    <Typography variant="h6" className={classes.title}>
                        Coin Scan
                    </Typography>
                    <Search/>
                </Toolbar>
            </AppBar>
        </div>
    );
}

export default Header;