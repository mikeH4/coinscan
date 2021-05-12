import Popper from '@material-ui/core/Popper';
import Fade from '@material-ui/core/Fade';
import Paper from '@material-ui/core/Paper';

import TokenCard from "../../components/Card/Card";

import styles from "./resultsStyles";

function ResultsPopover ({open,anchorEl,width = "fit-content"}) {
    const classes = styles();
    return (
        <Popper
        open={open}
        anchorEl={anchorEl}
        placement={"bottom-end"}
        transition
        >
            {({ TransitionProps }) => (
            <Fade {...TransitionProps} timeout={350}>
                <Paper className={classes.container} style={{width}}>
                    <TokenCard
                    token={{
                        address: "0xb7d053ba590a61100dfba0951182a6a50cd168cc",
                        symbol: "SAFEMOON",
                        name: "SafeMoon",
                        bscheck: "safe"
                    }}
                    flat={true}
                    />
                    <TokenCard
                    token={{
                        address: "0x68758923ca801f1c5b54ef78e0e16767a46a6131",
                        symbol: "CUMMIES",
                        name: "CumRocket",
                        bscheck: "risky"
                    }}
                    flat={true}
                    />
                </Paper>
            </Fade>
            )}
        </Popper>
    )
}
export default ResultsPopover;