import Container from "../reusable/Container";
import {
    BrowserRouter as ReactRouter,
    Switch,
    Route,
    useLocation
} from "react-router-dom";
  
import routes from "../routes";

const Router = ({Header}) => {
    return (
        <ReactRouter>
            <Header/>
            <Container dir="row">
                <Switch>
                    {routes.map(({Path,Render}) => (
                        <Route
                        key={Path}
                        path={Path}
                        component={Render}
                        />
                    ))}
                </Switch>                
            </Container>
        </ReactRouter>
    )
}
export default Router;

export const Query = (search = null) => {
    const locationQuery = useLocation().search;
    const searchQuery = search || locationQuery;
    return Object.fromEntries(new URLSearchParams(searchQuery).entries());
};