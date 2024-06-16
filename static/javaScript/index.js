function fetchMrts() {
    fetch('/api/mrts')
      .then((response) => response.json())
      .then((data) => {
        const ul = document.getElementById('mrt-stations');
        
        data.data.forEach((station) => {
          const li = document.createElement('li');
          li.textContent = station; 
          ul.appendChild(li);
  
          li.addEventListener('click', function () {
  
            const searchInput = document.getElementById('search-input');
            searchInput.value = station;
            const searchButton = document.getElementById('search-button');
            searchButton.click();         
          });
        });
      })
      .catch((error) => {
        console.error('無法顯示：', error);
      });
  }
  window.onload = fetchMrts;
  
  fetchMrts();
  
  function leftScroll() {
    const listContent = document.getElementById('mrt-stations');
    const scrollAmount = listContent.offsetWidth; 
    listContent.scrollLeft -= scrollAmount; 
  }
  
  function rightScroll() {
    const listContent = document.getElementById('mrt-stations');
    const scrollAmount = listContent.offsetWidth;
    listContent.scrollLeft += scrollAmount; 
  }
  
  function setupAttractionSearch() {
    document.addEventListener("DOMContentLoaded", function () {
      const searchButton = document.getElementById("search-button");
      const searchInput = document.getElementById("search-input");
      const attractionsContainer = document.getElementById("attractions-container");
      let nextPage = 0;
      let isLoading = false;
      let keyword = "";
  
      function loadMoreData() {
        if (nextPage !== null && !isLoading) {
          isLoading = true;
      
          fetch(`/api/attractions?keyword=${keyword}&page=${nextPage}`)
            .then((response) => response.json())
            .then((data) => {
              console.log(data)
              if (data.data && data.data.length > 0) {
                data.data.forEach((attraction) => {
                  appendDataToPage(attraction);
                });
      
                nextPage = data.nextPage;
      
                isLoading = false;
              } else if (data === null || data.data === null) {
                  window.alert("查無景點");
                  isLoading = false;
              } else {
                nextPage = null;
              }
            })
            .catch((error) => {
              console.error("Error:", error);
              isLoading = false;
            });
        }
      }
      
  function initializePage() {
    attractionsContainer.innerHTML = "";
    nextPage = 0;
    keyword = searchInput.value;
  
    setupScrollListener();
    loadMoreData();
  }
  
  function setupScrollListener() {
    window.addEventListener("scroll", function () {
      if (
        window.innerHeight + window.scrollY >=
          document.documentElement.scrollHeight - 100 &&
        nextPage !== null &&
        !isLoading
      ) {
        loadMoreData();
      }
    });
  }
  
  function appendDataToPage(attraction) {
    const attractionDiv = document.createElement("div");
    attractionDiv.classList.add("attraction");
  
    attractionDiv.onclick = function() {
      const attractionId = attraction.id;
      window.location.href = `/attraction/${attractionId}`;
    };
    
      if (attraction.images && attraction.images.length > 0) {
      const imgElement = document.createElement("img");
      imgElement.src = attraction.images[0];
      imgElement.alt = attraction.name;
      imgElement.classList.add("attraction-img");
      attractionDiv.appendChild(imgElement);
  }
      
    const textElement1 = document.createElement("div");
    textElement1.textContent = attraction.name;
    textElement1.classList.add("opacity", "attraction-name");
    attractionDiv.appendChild(textElement1);
      
    const imageBottom = document.createElement("div");
    imageBottom.classList.add("image-bottom");
    attractionDiv.appendChild(imageBottom);
      
    const textElement2 = document.createElement("div");
    textElement2.textContent = attraction.mrt;
    textElement2.classList.add("mrt-name");
    imageBottom.appendChild(textElement2);
      
    const textElement3 = document.createElement("div");
    textElement3.textContent = attraction.category;
    textElement3.classList.add("category");
    imageBottom.appendChild(textElement3);
    
    attractionsContainer.appendChild(attractionDiv);
  
  }
  
  window.onload = function () {
    initializePage();
    setupScrollListener(); 
  }
  
  searchButton.addEventListener("click", initializePage);
    });
  }
  
  setupAttractionSearch();
  
  
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
  
  function returnIndex(){
    window.location.href = `/`;
  }
  
  function bookingButton(){
    const token = localStorage.getItem("token");
    if (!token) {
      loginBlock();
    }
    else
    window.location.href = "/booking";
  }