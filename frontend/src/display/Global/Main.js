import React from 'react';

import { ThemeProvider } from '@material-ui/core/styles';
import useMediaQuery from '@material-ui/core/useMediaQuery';
import CssBaseline from "@material-ui/core/CssBaseline";

import Router from "./Router";
import { lightTheme, darkTheme } from './pallete';
import appStyles from './styles';
import Header from "./Header/Header";
import Sidebar from "./Sidebar/Sidebar";


const Main =  () => {
   const prefersDarkMode = useMediaQuery('(prefers-color-scheme: dark)');
   const classes = appStyles();

   return (
      <ThemeProvider theme={prefersDarkMode ? darkTheme : lightTheme}>
         <CssBaseline />
         <div className={classes.main}>
               <Router Header={Header} Sidebar={Sidebar}/>
         </div>
      </ThemeProvider>
   );
}
export default Main;