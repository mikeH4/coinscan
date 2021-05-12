import { makeStyles } from '@material-ui/core/styles';

const cardStyles = makeStyles((theme) => ({
   wrapper: {
      margin: theme.spacing(1) + "px 0",
   },
   flat: {
      margin: 0,
      boxShadow: "none"
   },
   card: ({turnToCol = 600}) => ({
      display: "flex",
      [theme.breakpoints.down(turnToCol)]: {
         flexDirection: 'column',
         height: "auto"
      },
      padding: 14,
      textDecoration: 'none !important',
      "& *": {
         textDecoration: 'none !important'
      },
   }),
   cardContent: {
      "&:nth-child(1)": {
         width: "100%"
      },
      "&:nth-child(2)": {
         width: "fit-content",
         display: "flex",
         alignItems: "center",
         padding: "0 10px !important",
         marginLeft: "auto"
      },
      padding: "0 !important",
   },
   name: {
      fontSize: "1.4em"
   },
   symbol: {
      textTransform: "uppercase",
      fontSize: "1em",
      color: "grey"
   },
   address: {
      marginTop: "5px",
      fontSize: ".95em"
   },
   bscheck: {
      fontSize: "1.4em",
      textTransform: "uppercase",
      fontWeight: 600
   },
   safe: {
      color: "rgb(0,168,107)"
   },
   warning: {
      color: "#f5c129"
   },
   risky: {
      color: "#ec8327"
   },
   scam: {
      color: "#f1444c"
   }
}));
export default cardStyles;