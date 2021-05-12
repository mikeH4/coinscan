import Popper from '@material-ui/core/Popper';
import Fade from '@material-ui/core/Fade';
import Paper from '@material-ui/core/Paper';

import TokenCard from "../../components/Card/Card";

import styles from "./resultsStyles";

function ResultsPopover ({open,anchorEl,width = "fit-content", results, loading}) {
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
                    {results.map(token => (
                        <TokenCard
                        token={token}
                        flat={true}
                        />
                    ))}
                </Paper>
            </Fade>
            )}
        </Popper>
    )
}
export default ResultsPopover;