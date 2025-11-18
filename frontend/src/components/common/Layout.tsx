/**
 * Main layout component with navigation
 */
import React from 'react';
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  useTheme,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Brightness4,
  Brightness7,
  Storage,
  Description,
  Search,
  Settings,
  CloudSync,
  Cable,
  Folder,
  CloudUpload,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import ProjectSelector from './ProjectSelector';

interface LayoutProps {
  children: React.ReactNode;
  onToggleTheme: () => void;
}

const drawerWidth = 240;

const menuItems = [
  { text: 'Configuration', icon: <Settings />, path: '/config' },
  { text: 'Projects', icon: <Folder />, path: '/projects' },
  { text: 'Stores', icon: <Storage />, path: '/stores' },
  { text: 'Documents', icon: <Description />, path: '/documents' },
  { text: 'RAG Query', icon: <Search />, path: '/query' },
  { text: 'Drive Sync', icon: <CloudSync />, path: '/drive' },
  { text: 'Drive Setup', icon: <CloudUpload />, path: '/drive-setup' },
  { text: 'LLM Integration', icon: <Cable />, path: '/integration' },
];

const Layout: React.FC<LayoutProps> = ({ children, onToggleTheme }) => {
  const [mobileOpen, setMobileOpen] = React.useState(false);
  const theme = useTheme();
  const navigate = useNavigate();
  const location = useLocation();

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const drawer = (
    <Box>
      <Toolbar>
        <Typography variant="h6" noWrap>
          File Search RAG
        </Typography>
      </Toolbar>
      <List>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton
              selected={location.pathname === item.path}
              onClick={() => {
                navigate(item.path);
                setMobileOpen(false);
              }}
            >
              <ListItemIcon>{item.icon}</ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar
        position="fixed"
        sx={{
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          ml: { sm: `${drawerWidth}px` },
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { sm: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            Google File Search RAG Application
          </Typography>
          <ProjectSelector />
          <IconButton color="inherit" onClick={onToggleTheme}>
            {theme.palette.mode === 'dark' ? <Brightness7 /> : <Brightness4 />}
          </IconButton>
        </Toolbar>
      </AppBar>
      <Box
        component="nav"
        sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
      >
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{ keepMounted: true }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          minHeight: '100vh',
        }}
      >
        <Toolbar />
        {children}
      </Box>
    </Box>
  );
};

export default Layout;
