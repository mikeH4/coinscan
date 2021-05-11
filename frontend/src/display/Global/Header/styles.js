import { makeStyles } from '@material-ui/core/styles';

const styles = makeStyles((theme) => ({
    root: { 
        flexGrow: 1,
    },
    toolbar: {
        padding: `1px ${theme.spacing(1)}px`,
        minHeight: 0
    },
    menuButton: {
        marginRight: theme.spacing(2),
    },
    title: {
        fontWeight: 400
    },
}));
export default styles;