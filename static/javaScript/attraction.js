const url = window.location.href;
const attractionId = url.substring(url.lastIndexOf('/') + 1);
let price = 2000;
let leftClicked = false;
let rightClicked = false;


function fetchAttractionData(attractionId) {
  fetch(`/api/attraction/${attractionId}`)
    .then((response) => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then((data) => {
      const attractionTitle = document.querySelector('.attraction-title');
      const attractionCategoryMRT = document.querySelector('.attraction-category-mrt');
      const infoIntro = document.querySelector('.info-intro');
      const infoAddress = document.querySelector('.info-address');
      const infoTraffic = document.querySelector('.info-traffic');
      const imageGallery = document.getElementById("imageGallery");
      
      if (data.error) {
        attractionTitle.textContent = 'Error';
        attractionCategoryMRT.textContent = data.message;
      } else {
        attractionTitle.textContent = data.data.name;
        attractionCategoryMRT.textContent = data.data.category + " at " + data.data.mrt;
        infoIntro.textContent = data.data.description;
        infoAddress.textContent = data.data.address;
        infoTraffic.textContent = data.data.transport;

        const attractionImages = data.data.images;
        
        attractionImages.forEach((imageUrl, index) => {
          const imgElement = document.createElement('img');
          imgElement.src = imageUrl;
          imgElement.alt = data.data.name;
          imgElement.classList.add('attraction-image');
          
          const dot = document.createElement('img');
          dot.src = "/static/images/circle.png";
          dot.classList.add('circle');

          dot.addEventListener('click', () => {
            showImage(index);
            setActiveDot(index);
          });

          dotContainer.appendChild(dot);
          imageGallery.appendChild(imgElement);

          if (index=== 0) {
            imgElement.style.display = "block";
            dot.src = "/static/images/circle-current.png";
          } else {
            imgElement.style.display = "none";
            dot.src = "/static/images/circle.png";
          }
        });
      }
    })
    .catch((error) => {
      console.error('Error fetching attraction data:', error);
    });
}
let currentImageIndex = 0;

function leftArrow() {
  const imageGallery = document.getElementById("imageGallery");
  const attractionImages = imageGallery.querySelectorAll(".attraction-image");
  const dots = document.querySelectorAll(".circle");
  
  attractionImages[currentImageIndex].style.display = "none";
  dots[currentImageIndex].src = "/static/images/circle.png";
  currentImageIndex = (currentImageIndex - 1 + attractionImages.length) % attractionImages.length;
  attractionImages[currentImageIndex].style.display = "block";
  dots[currentImageIndex].src = "/static/images/circle-current.png";
}

function rightArrow() {
  const imageGallery = document.getElementById("imageGallery");
  const attractionImages = imageGallery.querySelectorAll(".attraction-image");
  const dots = document.querySelectorAll(".circle");

  
  attractionImages[currentImageIndex].style.display = "none";
  dots[currentImageIndex].src = "/static/images/circle.png"; 
  currentImageIndex = (currentImageIndex + 1) % attractionImages.length;
  attractionImages[currentImageIndex].style.display = "block";
  dots[currentImageIndex].src = "/static/images/circle-current.png";
}

fetchAttractionData(attractionId);

function check_left() {
  price = 2000;
  leftClicked = true;
  document.getElementById("tourCost").textContent = "NTD 2000 ";
  document.getElementById("leftIconUnfilled").style.display = "none";
  document.getElementById("leftIconFilled").style.display = "block";
  
  document.getElementById("rightIconUnfilled").style.display = "block";
  document.getElementById("rightIconFilled").style.display = "none";
}

function check_right() {
  price = 2500;
  rightClicked = true;
  document.getElementById("tourCost").textContent = "NTD 2500 ";
  document.getElementById("rightIconUnfilled").style.display = "none";
  document.getElementById("rightIconFilled").style.display = "block";
  
  document.getElementById("leftIconUnfilled").style.display = "block";
  document.getElementById("leftIconFilled").style.display = "none";
}

function returnIndex(){
  window.location.href = `/`;
}


function loginBlock() {
  const loginForm = document.querySelector('.login-form');
  const registrationForm = document.querySelector(".registration-form");
  const loginClass = document.querySelector(".login-class")
  
  loginClass.style.display = "block";
  loginForm.style.display = 'block';
  registrationForm.style.display = "none";
}

function closeLoginForm() {
  const loginForm = document.querySelector('.login-form');
  const loginClass = document.querySelector(".login-class")
  loginClass.style.display = "none";
  loginForm.style.display = 'none';
}

function closeRegistForm() {
  const registrationForm = document.querySelector('.registration-form');
  const loginClass = document.querySelector(".login-class")
    
  loginClass.style.display = "none";
  registrationForm.style.display = 'none';
}

function switchToRegist() {
  const loginForm = document.querySelector('.login-form');
  const registrationForm = document.querySelector('.registration-form');

  loginForm.style.display = 'none';
  registrationForm.style.display = 'block';
}

function switchToLogin() {
  const loginForm = document.querySelector('.login-form');
  const registrationForm = document.querySelector('.registration-form');

  loginForm.style.display = 'block';
  registrationForm.style.display = 'none';
}

function submitSignupForm(signupEvent) {
  signupEvent.preventDefault();

  const signupNameInput = document.getElementById("signupName");
  const signupEmailInput = document.getElementById("signupEmail");
  const signupPasswordInput = document.getElementById("signupPassword");

  if (signupNameInput.value === "" || signupEmailInput.value === "" || signupPasswordInput.value === "") {
      const messageBox = document.querySelector(".message-box");
      messageBox.style.display = "block";
      messageBox.textContent = "Missing some field";
  } else {
      fetch("/api/user", {
          method: "POST",
          body: new FormData(document.getElementById("signupForm")),
      })
      .then((response) => response.json())
      .then((data) => {
          const messageBox = document.querySelector(".message-box");
          messageBox.textContent = data.message;

          if (data.error) {
              messageBox.style.color = "red";
              messageBox.style.display = "block";
          } else {
              messageBox.style.backgroundColor = "white";
              messageBox.style.color = "green";
              messageBox.style.display = "block";
          }
      })
      .catch((error) => {
          console.error("Error:", error);
      });
  }
}

function submitSigninForm(signinEvent) {
  signinEvent.preventDefault();

  const signinEmailInput = document.getElementById("signinEmail");
  const signinPasswordInput = document.getElementById("signinPassword");

  if (signinEmailInput.value === "" || signinPasswordInput.value === "") {
      const signinMessageBox = document.querySelector(".signin-message-box");
      signinMessageBox.style.display = "block";
      signinMessageBox.textContent = "Missing some field";
  } else {
      fetch("/api/user/auth", {
          method: "PUT",
          body: new FormData(document.getElementById("signinForm")),
      })
      .then((response) => response.json())
      .then((data) => {
          const signinMessageBox = document.querySelector(".signin-message-box");
          if (data.error) {
              signinMessageBox.style.color = "red";
              signinMessageBox.style.display = "block";
              signinMessageBox.textContent = data.message;
          } else {
              localStorage.setItem("token", data.token);
              const isLoggedIn = true;
              if (isLoggedIn) {
                window.location.reload();
              }
          }
      })
      .catch((error) => {
          console.error("Error:", error);
      });
  }
}

window.addEventListener('load', checkUserStatus);

function checkUserStatus() {
  const token = localStorage.getItem("token");
  const headers = token
    ? { Authorization: `Bearer ${token}` }
    : {}; 

  fetch('/api/user/auth', {
    method: 'GET',
    headers: headers
  })
    .then(response => {
      if (response.status === 200) {
        return response.json();
      } else {
        throw new Error('请求失败');
      }
    })
    .then(data => {
      const loginLink = document.getElementById('login-link');
      const logoutLink = document.getElementById('logout-link');

      if (data && data.data !== null) {
        loginLink.style.display = 'none';
        logoutLink.style.display = 'block';
      } else {
        loginLink.style.display = 'block';
        logoutLink.style.display = 'none';
      }
    })
    .catch(error => {
      console.error('獲取用戶時出現錯誤：', error);
    });
}

function logoutBlock() {
  localStorage.removeItem("token");  
  window.location.reload();
}

function bookTrip() {
  const date = document.getElementById("dateInput").value;
  const url = window.location.href;
  const attractionId = url.substring(url.lastIndexOf('/') + 1);
  const time = price === 2000 ? "morning" : "afternoon";

  const bookingData = {
      attractionId: attractionId,
      date: date,
      time: time,
      price: price
  };
  console.log(bookingData);

  const token = localStorage.getItem("token");
  const headers = token
      ? { Authorization: `Bearer ${token}` }
      : {};
  if (!token) {
    loginBlock();
  }
  else if (date === "" ) {
    alert("Missing some field")
  }
  else if (!leftClicked && !rightClicked){
    alert("Missing some field")
  }
  else {
  fetch("/api/booking", {
      method: "POST",
      headers: {
          "Content-Type": "application/json",
          ...headers
      },
      body: JSON.stringify(bookingData) 
  })
  .then(response => response.json())
  .then(data => {
      if (data.ok) {
          window.location.href = "/booking";
      }else {
        console.error("Error:"+data.message)
      }
  })
  .catch(error => {
      console.error("Error:", error);
  });
}
}

function bookingButton(){
  const token = localStorage.getItem("token");
  if (!token) {
    loginBlock();
  }
  else
  window.location.href = "/booking";
}