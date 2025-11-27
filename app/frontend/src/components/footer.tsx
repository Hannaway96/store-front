import { Box, Typography } from "@mui/material"

function Footer() {

    return (
        <>
        <Box className="footer">
            <Typography variant="body2" align="center" sx={{ py: 2, mt: 4, backgroundColor: '#93a1afff', color: 'white' }}>
                {'© '} Store Front {new Date().getFullYear()}
            </Typography>
        </Box>
        </>

    )
}

export default Footer