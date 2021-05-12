import Button from '@material-ui/core/Button';
import Tooltip from '@material-ui/core/Tooltip';
import Typography from '@material-ui/core/Typography';
import MaterialIcon from 'material-icons-react';
import { useState,useCallback } from 'react';

import styles from "./styles";


function CopyText ({text,className}) {
    const classes = styles();
    const [tooltipOpen,setTooltipOpen] = useState(false);

    const handleCopying = useCallback((text, event) => {
        event.stopPropagation();
        event.preventDefault();
        navigator.clipboard.writeText(text);
        setTooltipOpen(true);
        setTimeout(() => setTooltipOpen(false), 1000);
    });

    return (
        <Tooltip
        open={tooltipOpen}
        title="Copied"
        placement="top-end"
        >
            <Button
            className={classes.button}
            onMouseDown={handleCopying.bind(null, text)}
            onClick={handleCopying.bind(null, text)}
            onTouchStart={handleCopying.bind(null, text)}
            >
                    <Typography className={([className,classes.text]).join(" ")}>
                        {text}
                    </Typography>
                    <MaterialIcon icon="content_copy" size={14}/>
            </Button>
        </Tooltip>
    )
}

export default CopyText;