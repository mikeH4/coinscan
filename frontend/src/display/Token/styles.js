import { makeStyles } from '@material-ui/core/styles';

const styles = makeStyles((theme) => ({
    container: {
        margin: `${theme.spacing(1.5)}px !important`,
        marginTop: `${theme.spacing(2)}px !important`,
        fontSize: "1em",
        [theme.breakpoints.down('xs')]: {
            fontSize: "0.7em"
        }
    },
    name: {
        fontSize: "2.5em"
    },
    symbol: {
        fontSize: "1.1em",
        color: "grey"
    },
    price_container: {
        alignItems: "center",
        fontSize: "1.2em",
    },
    price: {
        fontSize: "2.5em",
    },
    price_symbol: {
        fontSize: "1em",
        marginLeft: "0.5em"
    }
}));
export default styles;