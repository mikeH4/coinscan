import { Typography } from "@material-ui/core";

import styles from "./styles";
import Container from "../../display/reusable/Container";

function Token () {
    const classes = styles();
    return (
        <Container width="100%" className={classes.container}>
            <Container dir="row" width="100%">
                <Container width="100%">
                    <Typography className={classes.name}>SafeMoon</Typography>
                    <Typography className={classes.symbol}>SAFEMOON</Typography>
                </Container>
                <Container dir="row" className={classes.price_container}>
                    <Typography className={classes.price}>0.089</Typography>
                    <Typography className={classes.price_symbol}>BNB</Typography>
                </Container>
            </Container>
        </Container>
    );
}
export default Token;