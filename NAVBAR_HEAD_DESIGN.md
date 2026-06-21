# Navbar & Head Section Design Guide

## Overview
The base.html template now features a modern, responsive navbar and professional head section with comprehensive styling for all pages.

## Features Implemented

### ✨ Head Section Enhancements
- **SEO Meta Tags**: description, keywords, author, and Open Graph tags
- **Responsive Viewport**: Optimized for all device sizes
- **Custom Favicon**: SVG-based favicon with brand logo
- **Google Fonts**: Inter font family for modern typography
- **CSS Variables**: Root variables for easy color customization

### 📱 Navbar Features
1. **Top Info Bar** (Optional, hidden on mobile)
   - Free shipping notification
   - Support contact information
   - Toggle-able visibility

2. **Main Navigation**
   - Logo with gradient background and smooth hover effects
   - Navigation links with animated underline on hover
   - Mobile-responsive hamburger menu
   - Search bar with rounded design

3. **User Features**
   - Wishlist icon with badge counter
   - Shopping cart icon with badge counter
   - User dropdown menu for authenticated users
   - Login/Register buttons for anonymous users
   - Animated gradient backgrounds

4. **Styling Highlights**
   - Smooth transitions and animations
   - Sticky positioning for easy access
   - Box shadows for depth
   - Gradient backgrounds for buttons
   - Icon-based navigation with hover states

### 📋 Footer Design
- **Company Information Section**
  - Logo, description, address, email, phone
  - Responsive multi-column layout

- **Quick Navigation Links**
  - Quick Links, Support, Policies sections
  - Social media integration with hover effects

- **Social Media Icons**
  - 5 major platforms (Facebook, Twitter, Instagram, LinkedIn, YouTube)
  - Animated hover effects with transform

## CSS Color Scheme

```css
:root {
    --primary-color: #0d6efd;        /* Blue */
    --primary-hover: #0b5ed7;         /* Darker Blue */
    --dark-bg: #0f1419;               /* Dark Background */
    --light-bg: #f8f9fa;              /* Light Background */
    --border-color: #e0e0e0;          /* Border */
    --text-dark: #1a1a1a;             /* Dark Text */
    --text-light: #666;               /* Light Text */
    --transition: all 0.3s ease;      /* Smooth Transitions */
}
```

## Responsive Breakpoints

| Device | Breakpoint | Changes |
|--------|-----------|---------|
| Desktop | 992px+ | Full navbar with search bar |
| Tablet | 576px - 991px | Collapsed menu, mobile optimized |
| Mobile | < 576px | Hamburger menu, stacked layout |

## Page-Specific Customization

### 1. Home Page (home.html)
```html
{% extends 'base.html' %}

{% block title %}Home - Astra Market{% endblock %}

{% block extra_css %}
<style>
    /* Hero section with gradient background */
    .hero-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 500px;
    }
</style>
{% endblock %}
```

### 2. Products Page (products.html)
```html
{% block extra_css %}
<style>
    /* Product grid styling */
    .product-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
        gap: 2rem;
    }
    
    .product-card {
        border: 1px solid var(--border-color);
        border-radius: 8px;
        transition: var(--transition);
    }
    
    .product-card:hover {
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
        transform: translateY(-4px);
    }
</style>
{% endblock %}
```

### 3. Product Detail Page (product_detail.html)
```html
{% block extra_css %}
<style>
    .product-detail-container {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 3rem;
        align-items: start;
    }
    
    .product-image {
        border-radius: 12px;
        overflow: hidden;
    }
    
    @media (max-width: 768px) {
        .product-detail-container {
            grid-template-columns: 1fr;
        }
    }
</style>
{% endblock %}
```

### 4. Cart Page (cart.html)
```html
{% block extra_css %}
<style>
    .cart-section {
        display: grid;
        grid-template-columns: 2fr 1fr;
        gap: 2rem;
    }
    
    .cart-item {
        border-bottom: 1px solid var(--border-color);
        padding: 1rem 0;
    }
    
    .order-summary {
        background: var(--light-bg);
        border-radius: 8px;
        padding: 1.5rem;
        position: sticky;
        top: 100px;
    }
    
    @media (max-width: 768px) {
        .cart-section {
            grid-template-columns: 1fr;
        }
        
        .order-summary {
            position: static;
        }
    }
</style>
{% endblock %}
```

### 5. Category Page (category.html)
```html
{% block extra_css %}
<style>
    .category-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: 1.5rem;
    }
    
    .category-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 8px;
        padding: 2rem;
        text-align: center;
        cursor: pointer;
        transition: var(--transition);
    }
    
    .category-card:hover {
        transform: scale(1.05);
    }
</style>
{% endblock %}
```

### 6. Checkout Page (checkout.html)
```html
{% block extra_css %}
<style>
    .checkout-container {
        display: grid;
        grid-template-columns: 2fr 1fr;
        gap: 2rem;
    }
    
    .form-section {
        background: white;
        padding: 2rem;
        border-radius: 8px;
        border: 1px solid var(--border-color);
    }
    
    .order-summary {
        background: var(--light-bg);
        padding: 1.5rem;
        border-radius: 8px;
        position: sticky;
        top: 100px;
        height: fit-content;
    }
    
    @media (max-width: 768px) {
        .checkout-container {
            grid-template-columns: 1fr;
        }
        
        .order-summary {
            position: static;
        }
    }
</style>
{% endblock %}
```

### 7. Login Page (login.html)
```html
{% block extra_css %}
<style>
    .auth-container {
        max-width: 400px;
        margin: 3rem auto;
        padding: 2rem;
        background: white;
        border-radius: 8px;
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
    }
    
    .auth-container h2 {
        text-align: center;
        margin-bottom: 1.5rem;
        color: var(--text-dark);
    }
</style>
{% endblock %}
```

### 8. User Profile Page (profile.html)
```html
{% block extra_css %}
<style>
    .profile-container {
        display: grid;
        grid-template-columns: 300px 1fr;
        gap: 2rem;
    }
    
    .profile-sidebar {
        background: white;
        padding: 2rem;
        border-radius: 8px;
        border: 1px solid var(--border-color);
        height: fit-content;
    }
    
    .profile-content {
        background: white;
        padding: 2rem;
        border-radius: 8px;
        border: 1px solid var(--border-color);
    }
    
    @media (max-width: 768px) {
        .profile-container {
            grid-template-columns: 1fr;
        }
    }
</style>
{% endblock %}
```

### 9. Orders Page (orders.html)
```html
{% block extra_css %}
<style>
    .orders-list {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }
    
    .order-card {
        background: white;
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 1.5rem;
        transition: var(--transition);
    }
    
    .order-card:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    }
    
    .order-status {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    
    .status-pending {
        background: rgba(255, 193, 7, 0.1);
        color: #856404;
    }
    
    .status-completed {
        background: rgba(25, 135, 84, 0.1);
        color: #155724;
    }
    
    .status-cancelled {
        background: rgba(220, 53, 69, 0.1);
        color: #721c24;
    }
</style>
{% endblock %}
```

## Alert Message Styling

The navbar supports styled alert messages with left border accents:

```html
<!-- Success Message -->
<div class="alert alert-success">Success message here</div>

<!-- Warning Message -->
<div class="alert alert-warning">Warning message here</div>

<!-- Error Message -->
<div class="alert alert-danger">Error message here</div>

<!-- Info Message -->
<div class="alert alert-info">Info message here</div>
```

## Breadcrumb Navigation

Add breadcrumbs to any page for better user navigation:

```html
<nav aria-label="breadcrumb">
    <ol class="breadcrumb">
        <li class="breadcrumb-item"><a href="{% url 'home' %}">Home</a></li>
        <li class="breadcrumb-item"><a href="{% url 'products' %}">Products</a></li>
        <li class="breadcrumb-item active">Product Name</li>
    </ol>
</nav>
```

## Customization Options

### Change Primary Color
Update the CSS variable in base.html:
```css
:root {
    --primary-color: #your-color-here;
    --primary-hover: #darker-shade-here;
}
```

### Add Custom Fonts
Update the Google Fonts import:
```html
<link href="https://fonts.googleapis.com/css2?family=YourFont:wght@300;400;500;600;700&display=swap" rel="stylesheet">
```

### Modify Navbar Padding
```css
.navbar {
    padding: 1rem 0; /* Increase for more vertical space */
}
```

## Key CSS Classes

| Class | Purpose |
|-------|---------|
| `.navbar` | Main navigation container |
| `.navbar-brand` | Logo and brand name |
| `.nav-link` | Navigation menu items |
| `.search-bar` | Search input container |
| `.nav-icon-link` | Cart/wishlist icons |
| `.user-avatar` | User profile badge |
| `.site-footer` | Footer container |
| `.footer-section` | Footer column sections |
| `.social-icons` | Social media link container |
| `.alert` | Message alert boxes |
| `.breadcrumb` | Breadcrumb navigation |

## Browser Compatibility
- Chrome (Latest)
- Firefox (Latest)
- Safari (Latest)
- Edge (Latest)
- Mobile Safari (iOS 12+)
- Chrome Mobile (Android 8+)

## Performance Optimizations
- CSS transitions use GPU acceleration (transform, opacity)
- Sticky navbar uses efficient positioning
- Responsive design prevents unnecessary rendering
- SVG favicon reduces HTTP requests
- Google Fonts loaded with display=swap for font performance

## Accessibility Features
- Semantic HTML structure
- ARIA labels for icon buttons
- Proper heading hierarchy
- Color contrast compliance
- Mobile-friendly touch targets
- Keyboard navigation support

## Notes
- All pages inherit the navbar and footer from base.html
- Each page can customize styles using `{% block extra_css %}`
- Use CSS variables for consistent theming
- Always test on mobile devices
- Follow the responsive breakpoints defined in base.html
