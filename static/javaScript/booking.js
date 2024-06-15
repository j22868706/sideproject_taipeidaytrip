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
        messageBox.textContent = "註冊失敗，有些欄位還沒填寫喔！";
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
        signinMessageBox.textContent = "登入失敗，有些欄位還沒填寫喔！";
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
        const usernamePlaceholder = document.getElementById("usernamePlaceholder");
  
        if (data && data.data !== null) {
          console.log(data)
          loginLink.style.display = 'none';
          logoutLink.style.display = 'block';
          usernamePlaceholder.textContent = data.data.name; 
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
  
  
  let bookingIdList = []
  let attractionNameList  = []
  let attractionAddressList  = []
  let attractionImgList  = []
  let bookingPriceList  = []
  let bookingDateList  = []
  let bookingTimeList = []
  
  
  document.addEventListener("DOMContentLoaded", function () {
  const token = localStorage.getItem("token");
  const headers = token
      ? { Authorization: `Bearer ${token}` }
      : {};
      if (!token) {
          returnIndex();
  }
  else
  fetch("/api/booking", {
      method: "GET",
      headers: {
          "Content-Type": "application/json",
          ...headers
      }
      })
  .then(response => response.json())
  .then(data => {
      console.log(data);
      const contactInfo = document.getElementById('contact-info');
      const paymentInfo = document.getElementById("payment-info");
      const payandcheck = document.getElementById("confirm-and-payment")
      const lineOne = document.getElementById("lineOne")
      const lineTwo = document.getElementById("lineTwo")
      const lineThree = document.getElementById("lineThree")
      const totalfee = document.getElementById("total-cost")
      const noReservation = document.getElementById('no-reservation')
      const attractionTitle = document.getElementById("attractionTitle")
      const attractionTime = document.getElementById("attractionTime")
      const attractionPrice = document.getElementById("attractiondPrice")
      const attractionAddress = document.getElementById("attractiondAddress")
      const attractionDate = document.getElementById("attractionDate")
      const attractionImg = document.getElementById("img")
      const section = document.getElementById("section")
  
  
      if (data && data.data !== null) {
        contactInfo.style.display = 'block';
        paymentInfo.style.display = 'block';
        payandcheck.style.display = 'block';
        noReservation.style.display = 'none'
        totalfee.textContent = data.data.price;
        attractionTitle.textContent = data.data.attraction.name;
        attractionDate.textContent = data.data.date;
        attractionTime.textContent = data.data.time; 
        attractionPrice.textContent = data.data.price; 
        attractionAddress.textContent = data.data.attraction.address;
        attractionImg.src = data.data.attraction.images;
        bookingIdList.push(data.data.attraction.id)
        attractionNameList.push(data.data.attraction.name)
        attractionAddressList.push(data.data.attraction.address)
        attractionImgList.push(data.data.attraction.images) 
        bookingPriceList.push(data.data.price) 
        bookingDateList.push(data.data.date) 
        bookingTimeList.push(data.data.time) 
  
      } else {
        contactInfo.style.display = 'none';
        paymentInfo.style.display = 'none';
        payandcheck.style.display = 'none';
        lineOne.style.display = 'none';
        lineTwo.style.display = 'none';
        lineThree.style.display = 'none';
        section.style.display = 'none';
      }
  })
  .catch(error => {
      console.error("Error fetching data:", error);
  });
  });
  
  function bookingButton(){
  const token = localStorage.getItem("token");
  if (!token) {
    loginBlock();
  }
  else
  window.location.href = "/booking";
  }
  
  function deleteBooking() {
  const token = localStorage.getItem("token");
  const headers = token ? { Authorization: `Bearer ${token}` } : {};
  
  fetch("/api/booking", {
    method: "DELETE",
    headers: headers,
  })
    .then((response) => response.json())
    .then((data) => {
      console.log(data)
      if (data.ok) {
        window.location.reload();
      } else {
        console.error("刪除預定失敗");
      }
    })
    .catch((error) => {
      console.error("發生錯誤:", error);
    });
  }
  
  window.onload = function () {
    TPDirect.setupSDK(137253, "app_8WLnvNV1WVzyJaxESUy0EMAHzxNm5EYXelGgT715zLEWRfRbLdAPnmanaASF", "sandbox")
    TPDirect.card.setup({
      fields: {
          number: {
              element: '.form-control.card-number',
              placeholder: '**** **** **** ****'
          },
          expirationDate: {
              element: document.getElementById('tappay-expiration-date'),
              placeholder: 'MM / YY'
          },
          ccv: {
              element: $('.form-control.ccv')[0],
              placeholder: 'CCV'
          }
      },
      styles: {
          'input': {
              'color': 'gray'
          },
          'input.ccv': {
              'font-size': '16px'
          },
          ':focus': {
              'color': 'black'
          },
          '.valid': {
              'color': 'green'
          },
          '.invalid': {
              'color': 'red'
          },
          '@media screen and (max-width: 400px)': {
              'input': {
                  'color': 'orange'
              }
          }
      },
      // 此設定會顯示卡號輸入正確後，會顯示前六後四碼信用卡卡號
      isMaskCreditCardNumber: true,
      maskCreditCardNumberRange: {
          beginIndex: 6, 
          endIndex: 11
      }
  })
  };
  
  let contactNameInputValue;
  let contactEmailInputValue;
  let contactPhoneInputValue;
  let bookingIsValidName = false;
  let bookingIsValidEmail = false;
  let bookingIsValidPhone = false;
  
  function handleNameInput() {
    const contactNameInput = document.getElementById("contact-name");
    contactNameInputValue = contactNameInput.value;
    if (contactNameInputValue === "") {
      bookingIsValidName = false;
      alert("姓名不能空白唷！！！"); 
    } else {
      bookingIsValidName = true;
    }
  }
  
  function handleEmailInput() {
    const contactEmailInput = document.getElementById("contact-email");
    contactEmailInputValue = contactEmailInput.value;
    if (contactEmailInputValue === "") {
      bookingIsValidEmail = false;
      alert("電子信箱忘記填了唷！！！"); 
    } else {
      bookingIsValidEmail = true;
    }
  }
  
  function handlePhoneInput() {
    const contactPhoneInput = document.getElementById("contact-phone");
    contactPhoneInputValue = contactPhoneInput.value;
    if (contactPhoneInputValue === "") {
      bookingIsValidPhone = false;
      alert("手機號碼不可以空白唷！！！"); 
    } else {
      bookingIsValidPhone = true;
    }
  }
  
  
  function onSubmit(event) {
      event.preventDefault();
      handleNameInput();
      handleEmailInput();
      handlePhoneInput();
  
      // 取得 TapPay Fields 的 status
      const tappayStatus = TPDirect.card.getTappayFieldsStatus();
  
      // 確認是否可以 getPrime
      if (tappayStatus.canGetPrime === false) {
          alert('無法獲取 Prime');
          return;
      }
  
      // Get prime
      TPDirect.card.getPrime((result) => {
        prime = result.card.prime
        trips = {
          attraction: {
            id: bookingIdList,
            name: attractionNameList,
            address: attractionAddressList,
            image: attractionImgList,
        },
        date: bookingDateList,
        time: bookingTimeList,
        }
      console.log(prime)
      const order_data = {
        prime: prime,
        order: {
            price: bookingPriceList,
            trip: trips,
            contact: {
                name: contactNameInputValue,
                email: contactEmailInputValue,
                phone: contactPhoneInputValue,
            },
        },
     };
     const token = localStorage.getItem("token");
     const headers = token
       ? { Authorization: `Bearer ${token}` }
       : {}; 
     fetch("/api/order", {
      method: "POST",
      headers: {
          "Content-Type": "application/json",
          ...headers
      },
      body: JSON.stringify(order_data),
     })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        const orderNumber = data.data.number
        const redirectURL = `/thankyou?number=${orderNumber}`;
        window.location.href = redirectURL;
        deleteBooking() 
    })
    .catch(error => {
        console.error('錯誤:', error);
    });
  });
  }