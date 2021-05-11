import { makeStyles } from '@material-ui/core/styles';

const styles = makeStyles((theme) => ({
    root: { 
        flexGrow: 1,
    },
    toolbar: {
        padding: `5px ${theme.spacing(1)}px`,
        minHeight: 0
    },
    menuButton: {
        marginRight: theme.spacing(1),
        padding: 6,
    },
    title: {
        fontWeight: 400,
        marginRight: theme.spacing(2),
        userSelect: "none",
        whiteSpace: "nowrap",
        [theme.breakpoints.down('xs')]: {
            display: "none"
        }
    },
}));
export default styles;