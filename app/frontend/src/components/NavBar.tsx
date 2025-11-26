import { AppBar, Toolbar, Typography, Container, Button } from "@mui/material";
import StorefrontIcon from '@mui/icons-material/Storefront';
import "./NavBar.css";

const NavBar = () => {
    return (

        <>
        <AppBar position="sticky" color="primary">
            <Container>
            <Toolbar>
                <StorefrontIcon sx={{ mr: 2 }} />
                <Typography variant="h5" sx={{flexGrow: 1, fontWeight: 'bold'}} >
                    Store Front
                </Typography>
                <Button color="inherit" href="#home">
                    Home
                </Button>
                <Button color="inherit" href="#products">
                    Products
                </Button>
            </Toolbar>
            </Container>
            </ AppBar>
        </>

    );
}

export default NavBar;