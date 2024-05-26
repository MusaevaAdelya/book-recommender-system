tailwind.config = {
      theme: {
        extend: {
          colors: {
            light: '#F5F6F8',
          }
        }
      }
    }

function checkImageSize(img) {
        if (img.naturalWidth === 1 && img.naturalHeight === 1) {
            img.src = 'https://www.shutterstock.com/image-vector/classical-book-cover-600nw-94690939.jpg';
            img.width = 103;

        }
    }

function handleProfileClick(){
    let dropdown=document.getElementById("user-dropdown-menu");
    dropdown.classList.toggle("hidden");
}

function changeProfilePicture(){
    let imageContainer = document.getElementById("profile-picture");
    // Assuming you have stored user information in localStorage
    const userInfoString = localStorage.getItem('user');
    if (!userInfoString) {
        imageContainer.src = "https://static.vecteezy.com/system/resources/previews/009/507/522/original/blue-avatar-sign-semi-flat-color-icon-customer-profile-anonymous-guest-full-sized-item-on-white-network-simple-cartoon-style-illustration-for-web-graphic-design-and-animation-vector.jpg";
        return;
    }

    const userInfo = JSON.parse(userInfoString);

    const profileImageUrl = userInfo.photoURL;

    imageContainer.src = profileImageUrl;
}

console.log("hello world")