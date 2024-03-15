
import { Box, Typography } from "@mui/material";
import { Link } from "react-router-dom";
import Button from "./elements/Button";



export const Banner = () => {
    return(
        <>
            <Box className="banner  mt-14 w-full px-7 mx-auto relative">
                <Box maxWidth="md" className="banner-head w-full p-3 mx-auto text-center">
                    <Typography variant="h1" sx={{ fontWeight: "bold", textTransform: "capitalize" }} className="topic pl-4 mt-0 text-white text-5xl gap">
                        Shorten URLs 
                        <span>
                            <Typography variant="h1" sx={{ color: "#BA2D0B", fontWeight: "bold" }} className="topic gap">
                                Scissor
                    </Typography></span> Shortener
                    </Typography>
                    <Typography variant="h6" paragraph sx={{ fontWeight: "light", fontSize:"16px", textAlign:"center" }} 
                        className="mt-1 pl-6 inner-text gap text-sm text-gray-400 py-1 text-xxl animate__animated animate__fadeIn animated__delay__4">
                        Create short links, QR Codes, and Link-in-bio pages. <br />
                        Share them anywhere. Track how well it&apos;s working.
                    </Typography>
                    <Box maxWidth="sm" className="pl-6 gap mx-auto">
                        <Link to="/shorten-link">
                            <Button className="mt-4">Start For Free</Button>
                        </Link>
                    </Box>
                </Box>
            </Box>    
        </>
    );
};

