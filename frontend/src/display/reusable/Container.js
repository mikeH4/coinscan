import { makeStyles } from '@material-ui/core/styles';

const styles = makeStyles((theme) => ({
    container: {
        display: "flex",
    },
    col: {
        flexDirection: "column",
        "& > *": {
            margin: `${theme.spacing(1)}px 0`
        },
        "& > *:first-child": {
            marginTop: "0"
        },
        "& > *:last-child": {
            marginBottom: "0"
        },
    },
    row: {
        flexDirection: "row",
        "& > *": {
            margin: `0 ${theme.spacing(1)}px`
        },
        "& > *:first-child": {
            marginLeft: "0"
        },
        "& > *:last-child": {
            marginRight: "0"
        },
    },
    extend: {
        flex: 1
    },
    pushRight: {
        marginLeft: "auto !important"
    }
}));

const Container = props => {
    const classes = styles();
    const dir = props.dir === "row" ? "row" : "col";
    const style = Object.assign(props.width ? {
        width: props.width
    } : {},props.style);


    const className = [
        classes.container,
        classes[dir],
        props.className || ""
    ];
    if (props.extend) {
        className.push(classes.extend);
    }
    if (props.push === "right") {
        className.push(classes.pushRight);
    }
    
    
    return (
        <div
        {...props}
        style={style}
        className={className.join(" ")}
        >
            {props.children}
        </div>
    )
}
export default Container;