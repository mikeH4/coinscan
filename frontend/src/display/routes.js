import Home from "./Home/Home";
import Token from "./Token/Token";

const routes = [
    {
        Path: "/token/:token",
        Render: Token
    },
    {
        Path: "/",
        Render: Home
    },
];
export default routes;