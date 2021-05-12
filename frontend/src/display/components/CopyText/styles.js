import { makeStyles } from '@material-ui/core/styles';

const cardStyles = makeStyles((theme) => ({
    button: {
        maxWidth: "100%"
    },
    text: {
        marginRight: 7,
        maxWidth: "100%",
        overflow: "hidden",
        textOverflow: "ellipsis"
    }
}));
export default cardStyles;