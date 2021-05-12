import { useState } from "react";
import TokenCard from "../components/Card/Card";
import Container from "../reusable/Container";

const Home = () => {
    const [items,setItems] = useState([]);
    const [loading,setLoading] = useState(false);
    return (
        <Container
        width="100%"
        dir="row"
        >
            <Container
            width="100%"
            style={{padding: 20}}
            >
                <TokenCard token={{
                    address: "0xb7d053ba590a61100dfba0951182a6a50cd168cc",
                    symbol: "SAFEMOON",
                    name: "SafeMoon",
                    bscheck: "scam"
                }}/>
                <TokenCard token={{
                    address: "0xb7d053ba590a61100dfba0951182a6a50cd168cc",
                    symbol: "SAFEMOON",
                    name: "SafeMoon",
                    bscheck: "scam"
                }}/>
            </Container>
        </Container>
    );
}
export default Home;