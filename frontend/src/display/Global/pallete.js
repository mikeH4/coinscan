import { createMuiTheme } from '@material-ui/core/styles';

const themeColor = "rgb(0,168,107)"

const global = {
    "@global": {
        "*::-webkit-scrollbar-thumb": {
            background: themeColor
        },
        "::-webkit-scrollbar": {
            background: "transparent",
            width: 4
        }
    },
    typography: {
        fontFamily: 'Raleway, Arial',
    },
    palette: {
        primary: {
            main: themeColor
        },
        secondary: {
            main: themeColor
        }
    } 
}

export const darkTheme = createMuiTheme(Object.assign(global,{
    name: "dark",
    type: "dark"
}));
export const lightTheme = createMuiTheme(Object.assign(global,{
    name: "light"
}));
