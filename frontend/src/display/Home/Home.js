import { useState } from "react";
import Container from "../reusable/Container";

const Home = () => {
    const [items,setItems] = useState([]);
    const [loading,setLoading] = useState(false);
    return (
        <Container
        width="100%"
        dir="row"
        >
            <Container extend={true}>
            </Container>
        </Container>
    );
}
export default Home;