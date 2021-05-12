import { createRef, useEffect, useState } from 'react';

import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import CardActionArea from '@material-ui/core/CardActionArea';
import Typography from '@material-ui/core/Typography';

import { Link } from 'react-router-dom';

import cardStyles from './styles';
import CopyText from "../CopyText/CopyText";

import clsx from "clsx";


const TokenCard = ({token, flat = false}) => {   
   const classes = cardStyles({turnToCol: flat ? 700 : 600});

    const {address, symbol, name, bscheck } = token;
    return (
       <Card className={clsx(classes.wrapper,{
          [classes.flat]: flat
       })}>
          <CardActionArea
          component={Link}
          to={`/token/${address}`}
          >
             <div className={classes.card}>
                <CardContent className={classes.cardContent}>
                   <Typography className={classes.name}>
                      {name}
                   </Typography>
                   <Typography className={classes.symbol}>
                      {symbol}
                   </Typography>
                   <CopyText className={classes.address} text={address}/>
                </CardContent>
                <CardContent className={classes.cardContent} >
                    <Typography className={classes.bscheck + " " + classes[bscheck]} >
                        {bscheck}
                   </Typography>
                </CardContent>
             </div>
          </CardActionArea>
       </Card>      
    );
}
export default TokenCard;