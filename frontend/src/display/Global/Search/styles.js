import { makeStyles, fade } from '@material-ui/core/styles';

const searchStyles = makeStyles((theme) => ({
   input: {
      marginLeft: theme.spacing(1),
      flex: 1,
      height: "100%"
   },
   searchWrapper: {
      width: "100%",
      flexDirection: "column"
   },
   search: {
      position: 'relative',
      backgroundColor: fade(theme.palette.common.white, 0.15),
      '&:hover': {
         backgroundColor: fade(theme.palette.common.white, 0.25),
      },
      marginRight: theme.spacing(1),
      marginLeft: "auto",
      flexGrow: 1,
      maxWidth: "600px",
   },
   searchIcon: {
      padding: theme.spacing(0, 2),
      height: '100%',
      position: 'absolute',
      pointerEvents: 'none',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
   },
   inputRoot: {
      color: 'inherit',
   },
   inputInput: {
      padding: theme.spacing(1, 1, 1, 0),
      // vertical padding + font size from searchIcon
      paddingLeft: `calc(1em + ${theme.spacing(4)}px)`,
      transition: theme.transitions.create('width'),
      width: '100%',
   },
}));

export default searchStyles;