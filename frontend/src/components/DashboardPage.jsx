import React, { useState, useEffect, useContext } from "react";
import { UserContext } from "../UserContext";
import { Box, Card, Typography, Container } from "@mui/material";
import axios from "axios";
import { Link } from "react-router-dom";

export function DashboardPage() {
    const { user } = useContext(UserContext);
    const [linkHistory, setLinkHistory] = useState([]);

    useEffect(() => {
        if (!user) {
            window.location.href="/login";
            return;
        }
        
        const fetchLinkHistory = async () => {
            try {
                const response = await axios.get(`http://localhost:8000/link-history/${user.id}`);
                setLinkHistory(response.data);
            } catch (error) {
                console.error("Error fetching link history:", error);
            }
        };

        fetchLinkHistory();
    }, [user]);

    return (
        <Box>
            <Box className="main_container my-14 mx-auto text-center md:px-6">
                <Container maxWidth="md" className="mt-14 text-white">
                    <Typography
                        variant="h2"
                        className="inline pl-8 mt-8 topic-md gap"
                        align="center"
                        sx={{
                            fontWeight: "bold",
                            marginTop: 6,
                            marginBottom: 3,
                        }}
                    >
                        Link &emsp;
                        <span>
                            <Typography
                                variant="h2"
                                className="inline text-toma"
                                sx={{
                                    fontWeight: "bold",
                                }}
                            >
                                History 
                            </Typography>
                        </span>
                    </Typography>
                </Container>
            </Box>
            <Card className="h-full w-full overflow-scroll">
                <table className="w-full min-w-max table-auto text-left">
                    <thead>
                        <tr>
                            <th className="border-b border-blue-gray-100 bg-[#C0E0DE] p-4">
                                <Typography
                                    variant="small"
                                    color="blue-gray"
                                    className="font-normal leading-none opacity-70"
                                >
                                    Original URL
                                </Typography>
                            </th>
                            <th className="border-b border-blue-gray-100 bg-[#C0E0DE] p-4">
                                <Typography
                                    variant="small"
                                    color="blue-gray"
                                    className="font-normal leading-none opacity-70"
                                >
                                    Shortened Link
                                </Typography>
                            </th>
                            <th className="border-b border-blue-gray-100 bg-[#C0E0DE] p-4">
                                <Typography
                                    variant="small"
                                    color="blue-gray"
                                    className="font-normal leading-none opacity-70"
                                >
                                    Visit Count
                                </Typography>
                            </th>
                            <th className="border-b border-blue-gray-100 bg-[#C0E0DE] p-4">
                                <Typography
                                    variant="small"
                                    color="blue-gray"
                                    className="font-normal leading-none opacity-70"
                                >
                                    Times Visited
                                </Typography>
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        {linkHistory.map((link, index) => (
                            <tr key={index} className={index % 2 === 0 ? "bg-blue-gray-50" : ""}>
                                <td className="p-4 border-b border-blue-gray-50">
                                    <Typography variant="small" color="blue-gray" className="font-normal">
                                        {link.original_url}
                                    </Typography>
                                </td>
                                <td className="p-4 border-b border-blue-gray-50">
                                    <Link to={`http://localhost:8000/${link.shortened_url}`} target="_blank">
                                        <Typography variant="small" className="font-normal text-blu hover:text-toma">
                                            {link.shortened_url}
                                        </Typography >
                                    </Link>
                                        
                                </td>
                                <td className="p-4 border-b border-blue-gray-50">
                                    <Typography variant="small" color="blue-gray" className="font-normal">
                                        {link.visit_count}
                                    </Typography>
                                </td>
                                <td className="p-4 border-b border-blue-gray-50">
                                    <Typography variant="small" color="blue-gray" className="font-normal">
                                        {link.times_visited.map((time, index) => (
                                            <ul>
                                                <li key={index}>{time}</li>
                                            </ul>
                                        ))}
                                    </Typography>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </Card>
        </Box>
    );
}
