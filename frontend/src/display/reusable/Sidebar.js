import { makeStyles } from '@material-ui/core/styles';
import Container from "./Container";

const styles = makeStyles((theme) => ({
    sidebar: {
        maxWidth: "35%"
    },
}));

const Sidebar = (props) => {
    const classes = styles();

    return (
        <Container
        {...props}
        className={[classes.sidebar,props.className || ""].join(" ")}
        />
    );
}
export default Sidebar;