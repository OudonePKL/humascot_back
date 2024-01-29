const access_token = localStorage.getItem('access_token')  //요청시 필요한 토큰 값
let lastClickedDt = null; // 모달 선택한 요소 저장

window.onload = async function () {
    let storeId = localStorage.getItem('store_id')
    if (!storeId) {
        alert('판매자만 이용가능합니다.')
        window.location.href = '/store/goods/list'
    }
    const response = await fetch(`${backend_base_url}/store/${storeId}`, {
        headers: {
            'content-type': 'application/json', "Authorization": `Bearer ${access_token}`,
        }, method: 'GET',
    });
    let response_json = await response.json()
    let registrationPath = staticPath + 'icon/registration.svg';
    if (response.ok) {
        if (response_json['goods_set'].length === 0) {
            document.getElementById('admin_goods_empty').style.display = 'block';
            document.getElementById('admin_goods_btn').className = 'btn on';
            document.getElementById('admin_goods_btn').innerText = '등록';
        } else {
            response_json['goods_set'].forEach((data) => {
                let name = data['name']
                let category = data['category']
                let description = data['description']
                let price = data['format_price']
                let image = data['image_set'][0]
                let order_set = data['order_set']
                let review_set = data['review_set']
                if (!image) {
                    image = staticPath + 'thum.png';
                }
                let star_avg = data['star_avg'];  // 나중에 아이콘 개수 맞추기
                star_avg = star_avg / 5 * 100
                if (star_avg === 0) {
                    star_avg = 100
                }
                let temp_html = `
                        <li id="goods_${data['goods_id']}" class="goods-card">
                            <div class="admin_thum">
                                <img src="${image}"
                                     alt=""/>
                            </div>
                            <div class="info mt20">
                                <div class="star">
                                    <div class="on" style="width: ${star_avg}%;"></div>
                                </div>
                                <div class="flex">
                                    <div class="category">${category}</div>
                                    <div class="cost">${price}</div>
                                </div>
                                <div class="name">${name}</div>
                                <p class="description goods_description" >${description}</p>
                            </div>
                        </li>
                `

                $('#admin_goods_list').append(temp_html);

                // 주문 카테고리 설정 -> 주문 없는 애들도 붙여야 하나?
                let order_goods_select_html2 = `
                        <li value="goods_id_${data['goods_id']}">${name}</li>
                `;
                $('.order_goods_select').append(order_goods_select_html2);
                $('.order_goods_select').on('click', 'li', function () {
                    var selectedValue = $(this).attr('value');
                    var change_filter = $(this).text();
                    document.getElementById('textToShow').innerText = change_filter;
                    filterOrderList(selectedValue);
                });

                // 리뷰 카테고리 설정 -> 리뷰 없는 애들도 붙여야 하나?
                let review_goods_select_html2 = `
                        <li value="reveiw_goods_id_${data['goods_id']}">${name}</li>
                `;
                $('.review_goods_select').append(review_goods_select_html2);
                $('.review_goods_select').on('click', 'li', function () {
                    var selectedValue2 = $(this).attr('value');
                    var change_filter2 = $(this).text();
                    document.getElementById('textToShow2').innerText = change_filter2;
                    filterReviewList(selectedValue2)
                    const moreButton = document.getElementById("moreButton");
                    // moreButton.style.display = "block";
                    // removeMoreButtons()
                    // test()
                    updateMoreButton()
                });

                // 주문 리스트 로드
                orderList(order_set);

                // 리뷰 리스트 로드
                reviewList(review_set, image);
            });

            let temp_html2 = `
                            <li onclick="addGoodsCard()" id="add_goods" style="display:none;">
                                <div class="plus">
                                    <img src="${registrationPath}" alt=""/>
                                </div>
                            </li>
            `
            $('#admin_goods_list').append(temp_html2);

            document.getElementById('admin_goods_btn').className = 'btn on';
            document.getElementById('admin_goods_btn').innerText = '수정';

            // 버튼 클릭시 수정 카드로
            await changeGoodsCard()
        }
    }

};


async function changeGoodsCard() {
    // 수정 버튼 클릭시 이벤트 추가
    $('#admin_goods_btn').click(function () {
        // 페이지의 모든 카드를 선택
        $('.goods-card').each(function () {
            // 현재 카드의 데이터 가져오기
            let goodsId = $(this).attr('id').split('_')[1];
            let name = $(this).find('.name').text();
            let category = $(this).find('.category').text();
            let price = $(this).find('.cost').text();
            price = price.replace(/,/g, '').replace('원', '');
            let description = $(this).find('.goods_description').text();
            let image = $(this).find('img').attr('src');

            // 새로운 카드 구조로 업데이트
            let temp_html = `
                    <li class="origin_goods" id="goods_${goodsId}">
                        <div class="thum">
                            <input id="goods_image_${goodsId}" class="file origin_card_input" type="file" multiple accept=".jpg, .png, .jpeg"/>
                            <label class="label" for="goods_image_${goodsId}" style="background: url(${image});" ></label>
                        </div>
                        <div class="info">
                            <dl class="goods_name">
                                <dt>${name}</dt>
                                <dd>
                                    <button class="modal-button">입력</button>
                                </dd>
                            </dl>
                            <dl class="goods_category">
                                <dt>${category}</dt>
                                <dd>
                                    <button class="modal-button">입력</button>
                                </dd>
                            </dl>
                            <dl class="goods_price">
                                <dt>${price}</dt>
                                <dd>
                                    <button class="modal-button">입력</button>
                                </dd>
                            </dl>
                            <dl class="goods_description">
                                <dt>${description}</dt>
                                <dd>
                                    <button class="modal-button">입력</button>
                                </dd>
                            </dl>
                            <dl class="goods_delete" style="justify-content: center;">
                                <dt onclick="creatDeleteModal(${goodsId})">삭제</dt>
                            </dl>
                        </div>
                    </li>
                `

            $(this).replaceWith(temp_html);
            creatModal();
            // 이미지 추가시 배경에 넣는 코드
            $('.file').change(function () {
                updateLabelBackground(this); // 파일이 변경될 때 함수 호출
            });
            fileLoadImage('origin')
        });
    });

}

async function creatModal() {
    // $('#admin_goods_list').append(temp_html);
    // 모든 "입력" 버튼에 이벤트 리스너 추가
    const closeModal = document.getElementById("close-modal");
    const modal = document.querySelector(".modal-wrapper");
    $('.modal-button').on('click', function () {
        document.getElementById('goods_input').style.display = 'block'

        let dlClass = $(this).closest('dl').attr('class'); // 현재 버튼이 속한 dl의 클래스 값
        lastClickedDt = $(this).closest('dl').find('dt')[0];
        if (dlClass === 'goods_name') {
            document.getElementById('modal_title').innerHTML = '선택하신 상품의 <br>' + '<span>상품명</span>을 입력해 주세요';
            document.getElementById('input_goods_info').placeholder = '상품명 입력';
        } else if (dlClass === 'goods_category') {
            document.getElementById('modal_title').innerHTML = '선택하신 상품의  <br>' + '<span>카테고리</span>를 입력해 주세요';
            document.getElementById('input_goods_info').placeholder = '카테고리 입력';
        } else if (dlClass === 'goods_price') {
            document.getElementById('modal_title').innerHTML = '선택하신 상품의  <br>' + '<span>가격</span>을 입력해 주세요';
            document.getElementById('input_goods_info').placeholder = '가격 입력';
            document.getElementById('input_goods_info').type = 'number';
        } else if (dlClass === 'goods_description') {
            document.getElementById('modal_title').innerHTML = '선택하신 상품의 <br>' + '<span>상품 설명</span>을 입력해 주세요';
            let inputElement = document.getElementById('input_goods_info');
            let textareaElement = document.createElement('input');

            // 필요한 경우, input 요소의 속성을 복사합니다.
            textareaElement.value = inputElement.value;
            textareaElement.placeholder = '상품 설명';
            textareaElement.id = inputElement.id;
            textareaElement.name = inputElement.name;

            inputElement.parentNode.replaceChild(textareaElement, inputElement);

        }
        document.getElementById('save_modal').onclick = function () {
            changeGoodsInfo();
        };
        modal.style.display = "flex"; // 모달 표시
    });


    closeModal.onclick = () => {
        modal.style.display = "none";
        let originElement = document.getElementById('input_goods_info');
        let inputElement = document.createElement('input');

        // input 태그로 변환
        inputElement.value = '';
        inputElement.id = originElement.id;
        inputElement.name = originElement.name;

        originElement.parentNode.replaceChild(inputElement, originElement);

    };
}

async function addGoodsCard() {
    let registrationPath = staticPath + 'icon/registration.svg';
    let temp_html = `
                            <li class="new_goods">
                                <div class="thum">
                                    <label class="label new_card_label">
                                        <input class="file new_card_file" type="file"  multiple accept=".jpg, .png, .jpeg"/>
                                    </label>
                                </div>
                                <div class="info">
                                    <dl class="goods_name">
                                        <dt>상품명</dt>
                                        <dd>
                                            <button class="modal-button">입력</button>
                                        </dd>
                                    </dl>
                                    <dl class="goods_category">
                                        <dt>카테고리</dt>
                                        <dd>
                                            <button class="modal-button">입력</button>
                                        </dd>
                                    </dl>
                                    <dl class="goods_price">
                                        <dt>가격</dt>
                                        <dd>
                                            <button class="modal-button">입력</button>
                                        </dd>
                                    </dl>
                                    <dl class="goods_description">
                                        <dt>상품 설명</dt>
                                        <dd>
                                            <button class="modal-button">입력</button>
                                        </dd>
                                    </dl>
                                   <dl className="goods_delete"  style="justify-content: center;">
                                        <dt onClick="deleteCard(event)">삭제</dt>
                                    </dl>
                                </div>
                            </li>
                `
    $('#admin_goods_list').append(temp_html);

    $('#add_goods').remove();
    let temp_html2 = `
                            <li onclick="addGoodsCard()" id="add_goods" style="display:block;">
                                <div class="plus">
                                    <img src="${registrationPath}" alt=""/>
                                </div>
                            </li>
            `
    $('#admin_goods_list').append(temp_html2);
    // 모달
    await creatModal()
    // 이미지 추가시 배경에 넣는 코드
    $('.file').change(function () {
        updateLabelBackground(this); // 파일이 변경될 때 함수 호출
    });

    await fileLoadImage('new')
}

function fileLoadImage(category) {
    if (category === 'new') {
        document.querySelectorAll('.file.new_card_file').forEach(function (fileInput) {
            fileInput.addEventListener('change', function (event) {
                const label = event.target.closest('.label');
                console.log(293)
                if (label) {
                    label.classList.add('background-cover');
                }
            });
        });
    } else if (category === 'origin') {
        document.querySelectorAll('.file.origin_card_input').forEach(function (fileInput) {
            fileInput.addEventListener('change', function (event) {
                console.log(301)
                const label = event.target.closest('.label');
                if (label) {
                    label.classList.add('background-cover');
                }
            });
        });
    }

}


async function changeBtn(category = null) {
    let btn = document.getElementById('admin_goods_btn');
    if (category === 1) {
        btn.style.display = 'block';
        return
    } else if (category === 2) {
        btn.style.display = 'none';
        document.getElementById('tab03').style.display = 'block';
        filterOrderList('0')
        return
    }
    let empty_icon = document.getElementById('admin_goods_empty');
    let empty_icon2 = document.getElementById('admin_goods_empty_2');
    let goods_list = document.getElementById('admin_goods_list');
    let add_goods = document.getElementById('add_goods');
    let origin_goods = document.querySelector('.origin_goods');
    let new_goods = document.querySelector('.new_goods');
    if (btn.innerText === '등록' | btn.innerText === '수정') {

        btn.innerText = '완료';
        btn.className = 'btn complete';
        if (goods_list.innerText) {
            empty_icon2.style.display = 'none';
            empty_icon.style.display = 'none';
            add_goods.style.display = 'block';
            return
        }
        if (empty_icon.style.display === 'block') {
            empty_icon2.style.display = 'block';
            empty_icon.style.display = 'none';
        }

    } else if (btn.innerText === '완료' || btn.innerText === '') {
        if (goods_list.innerText) {
            let _confirm = confirm('이미지 수정시 기존 상품의 이미지는 모두 삭제 됩니다.\n수정하시겠습니까?')
            if (!_confirm) {
                return false
            }
            let create_goods = await createGoodsInfo()
            if (create_goods === false) {
                return
            } else {
                await patchGoodsInfo()
                window.location.reload()
            }
            btn.className = 'btn on';
            btn.innerText = '수정';
            empty_icon2.style.display = 'none';
            empty_icon.style.display = 'none';
            add_goods.style.display = 'none';
            return
        }
        if (empty_icon.style.display === 'none') {
            btn.innerText = '등록';
            empty_icon2.style.display = 'none';
            empty_icon.style.display = 'block';
            await createGoodsInfo()
        }
    }
}


async function changeGoodsInfo() {
    const modal = document.querySelector(".modal-wrapper");
    let data = document.getElementById('input_goods_info');
    let inputElement = document.createElement('input');
    // 마지막으로 클릭된 "입력" 버튼에 데이터 설정
    if (lastClickedDt) {
        // $(lastClickedDt).innerText = data; // 여기서는 버튼의 텍스트로 데이터를 설정합니다.
        $(lastClickedDt).text(data.value);
    }

    // 모달 숨기기
    modal.style.display = "none";

    // input 태그로 변환
    inputElement.value = '';
    inputElement.id = data.id;
    inputElement.name = data.name;

    data.parentNode.replaceChild(inputElement, data);
}


async function patchGoodsInfo() {
    let goods_set = [];

    // 모든 상품에 대한 처리를 담을 프로미스 배열
    let promises = $('.origin_goods').map(async function () {
        let currentElement = $(this);
        let goods_id = currentElement.closest('li').attr('id').split('_')[1];

        // 이미지 한번에 여러개 선택 가능 -> 문구 줘야할 듯
        // 이미지 수정시 기존 이미지 모두 삭제 되고, 새로운 사진으로 채워짐
        let imageFiles = document.getElementById(`goods_image_${goods_id}`).files
        let imagePromises = Array.from(imageFiles).map(file => convertToBase64(file));
        let imageSet = await Promise.all(imagePromises);
        let goodsInfo = {
            id: goods_id,
            category: currentElement.find('.goods_category dt').text(),
            name: currentElement.find('.goods_name dt').text(),
            price: currentElement.find('.goods_price dt').text(),
            description: currentElement.find('.goods_description dt').text(),
            images: imageSet
        };

        return goodsInfo;
    }).get();

    goods_set = await Promise.all(promises);

    // 서버에 전송
    const response = await fetch(`${backend_base_url}/store/goods`, {
        method: 'PATCH', headers: {
            "Authorization": `Bearer ${access_token}`, "Content-Type": "application/json"
        }, body: JSON.stringify({goods_set})
    });

}


async function createGoodsInfo() {
    let goods_set = [];
    // 모든 상품에 대한 처리를 담을 프로미스 배열
    let new_goods = document.querySelector('.new_goods');
    let promises = $('.new_goods').map(async function () {
        let currentElement = $(this);

        // 이미지 한번에 여러개 선택 가능 -> 문구 줘야할 듯
        // 이미지 수정시 기존 이미지 모두 삭제 되고, 새로운 사진으로 채워짐
        let imageFiles = currentElement.find('.file')[0].files
        let imagePromises = Array.from(imageFiles).map(file => convertToBase64(file));
        let imageSet = await Promise.all(imagePromises);
        let goodsInfo = {
            category: currentElement.find('.goods_category dt').text(),
            name: currentElement.find('.goods_name dt').text(),
            price: currentElement.find('.goods_price dt').text(),
            description: currentElement.find('.goods_description dt').text(),
            images: imageSet
        };

        if (goodsInfo.category === '' || goodsInfo.name === '' || goodsInfo.price === '' || goodsInfo.images.length === 0 || goodsInfo.category === '카테고리' || goodsInfo.name === '상품명' || goodsInfo.price === '가격') {
            document.getElementById('error_msg').innerText = '모든 필수 요소를 채워주세요(이미지, 상품명, 카테고리, 가격)'
            document.getElementById('error_msg').style.display = 'block'
            return false
        }

        return goodsInfo;
    }).get();

    goods_set = await Promise.all(promises);
    if (!goods_set[0] && new_goods) {
        return false
    }
    if (goods_set.length !== 0) {
        let store_id = localStorage.getItem('store_id')
        // 서버에 전송
        const response = await fetch(`${backend_base_url}/store/${store_id}`, {
            method: 'POST', headers: {
                "Authorization": `Bearer ${access_token}`, "Content-Type": "application/json"
            }, body: JSON.stringify({goods_set})
        });

    }
}


// 이미지 base64로 변환
function convertToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = reject;
        reader.readAsDataURL(file);
    });
}

function updateLabelBackground(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();

        reader.onload = function (e) {
            // 해당 input과 연관된 label의 배경 이미지 설정
            if ($(input).closest('.label').length === 0) {
                $(input).next('label').css('background', 'url(' + e.target.result + ')');
            } else {
                $(input).closest('.label').css('background', 'url(' + e.target.result + ')');
            }
        };

        reader.readAsDataURL(input.files[0]); // 파일 읽기 시작
    }
}


async function orderList(order_set) {
    order_set.forEach((data) => {
        let goods_id = data['goods']
        let user_name = data['user_name']
        let goods_name = data['goods_name']
        let ordered_at = data['ordered_at']
        let temp_html = `
        <li class="goods_id_${goods_id}">
            <div>
                <span class="name">'${user_name}'</span>님이
                <span class="product">${goods_name}</span> 상품을
                주문했어요.
            </div>
            <span class="day">${ordered_at}</span>
        </li>
`
        $('#order_list').append(temp_html)
    })
}

function filterOrderList(selectedValue) {
    $("#order_list li").css("display", "none");

    if (selectedValue === '0') {
        $("#order_list li").css("display", "block");

    } else {
        $("#order_list li." + selectedValue).css("display", "block");
    }
}


function reviewList(review_set, image) {
    review_set.forEach((data) => {
        let goods_id = data['goods_id']
        let created_at = data['created_at']
        let user_name = data['user_name']
        let review = data['review']
        let star = data['star']
        let user_profile = data['user_profile']
        star = star / 5 * 100
        let temp_html = ''
        if (user_profile !== 'false' && user_profile !== null) {
            temp_html = `
                <li class="reveiw_goods_id_${goods_id} review-box">
                    <div class="thum" style="background: url(${image}); background-size: cover;">
                    </div>
                    <div class="info">
                        <div class="flex">
                            <div class="user">
                                <div class="img">
                                    <img class="review_img" src="${user_profile}" alt=""/>
                                </div>
                                <div class="txt">
                                    ${user_name}
                                    <div class="star">
                                        <div class="on" style="width: ${star}%"></div>
                                    </div>
                                </div>
                            </div>
                            <span class="day">${created_at}</span>
                        </div>
                        <p class="review-content">${review}</p>
                    </div>
                </li>
            `
        } else {
            user_profile = staticPath + 'icon/profile.svg'
            temp_html = `
                <li class="reveiw_goods_id_${goods_id} review-box">
                    <div class="thum" style="background: url(${image}); background-size: cover;">
                    
                    </div>
                    <div class="info">
                        <div class="flex">
                            <div class="user">
                                <div class="img empty02">
                                    <img src="${user_profile}" alt=""/>
                                </div>
                                <div class="txt">
                                    ${user_name}
                                    <div class="star">
                                        <div class="on" style="width: ${star}%"></div>
                                    </div>
                                </div>
                            </div>
                            <span class="day">${created_at}</span>
                        </div>
                        <p class="review-content">${review}</p>
                    </div>
                </li>
            `
        }

        $('#review_list').append(temp_html)
    })
    filterReviewList('0'); // '더보기' 버튼 상태 업데이트
}

function updateMoreButton() {
    const moreButton = document.getElementById("moreButton");
    let currentIndex = 8;

    // 필터링된 리뷰가 8개 이하인 경우, '더보기' 버튼 숨김
    if (currentFilteredReviews.length <= 8) {
        moreButton.style.display = "none";
    } else {
        moreButton.style.display = "block";

        moreButton.onclick = function () {
            let maxIndex = Math.min(currentIndex + 8, currentFilteredReviews.length);
            for (let i = currentIndex; i < maxIndex; i++) {
                currentFilteredReviews[i].style.display = "flex";
                loadReviews();
            }

            currentIndex += 8;
            if (currentIndex >= currentFilteredReviews.length) {
                moreButton.style.display = "none";
            }
        };
    }
}


let currentFilteredReviews = []; // 현재 필터링된 리뷰 항목들을 저장할 배열
function filterReviewList(selectedValue) {
    let allReviews = $("#review_list li");
    allReviews.hide(); // 모든 리뷰를 숨깁니다.

    if (selectedValue === '0') {
        currentFilteredReviews = Array.from(allReviews);
    } else {
        currentFilteredReviews = Array.from(allReviews.filter("." + selectedValue));
    }

    currentFilteredReviews.slice(0, 8).forEach(li => li.style.display = 'flex');

    updateMoreButton(); // '더보기' 버튼 상태 업데이트
    loadReviews();       // 새로운 버튼 추가
}


async function createFirstGoods() {
    let registrationPath = staticPath + 'icon/registration.svg';
    let empty_icon2 = document.getElementById('admin_goods_empty_2');
    if (empty_icon2.style.display === 'block') {
        empty_icon2.style.display = 'none';
    }
    await addGoodsCard();
}

async function loadReviews() {
    removeMoreButtons()
    let review_active = document.getElementById('reivew_link');
    let style = window.getComputedStyle(review_active);
    let backgroundColor = style.backgroundColor;


    document.getElementById('tab03').style.display = 'block';

    $('.review-box').each(function () {
        var content = $(this).find('.review-content');
        var maxHeight = 60; // 설정한 최대 높이
        var btn_more = $('<a href="javascript:void(0)" id="more_btn" class="more">...더보기</a>');
        $(this).find('.info').append(btn_more);
        if (content[0].offsetHeight > maxHeight) {
            content.css('max-height', maxHeight + 'px');
            content.css('overflow', 'hidden');
        } else {
            btn_more.hide();
        }

        btn_more.click(function () {
            if (content.css('max-height') !== 'none') {
                $(this).html('...접기');
                content.css('max-height', 'none');
            } else {
                $(this).html('...더보기');
                content.css('max-height', maxHeight + 'px');
            }
        });
    });

    if (backgroundColor !== 'rgb(255, 79, 22)') {
        document.getElementById('tab03').style.display = 'none';
    }
}

function removeMoreButtons() {
    $('.review-box').each(function () {
        // 각 리뷰 박스에서 "더보기" 버튼을 찾고 제거
        var btn_more = $(this).find('.more');
        if (btn_more.length) {
            btn_more.remove();
        }

        // 리뷰 콘텐츠의 max-height 스타일 초기화
        var content = $(this).find('.review-content');
        content.css('max-height', '');
        content.css('overflow', '');
    });
}


async function creatDeleteModal(goods_id) {
    const modal = document.querySelector(".modal-wrapper");
    document.getElementById('goods_input').style.display = 'none';
    document.getElementById('modal_title').style.display = 'block';
    document.getElementById('modal_title').innerHTML = '상품을 <span class="ty03">삭제</span>하시겠습니까?\n' +
        '                    <small>삭제된 상품은 복구되지 않습니다.</small>';
    document.getElementById('save_modal').style.display = 'block';
    modal.style.display = "flex"; // 모달 표시
    document.getElementById('save_modal').onclick = function () {
        deleteGoods(goods_id);
    };
}

async function deleteGoods(goods_id) {
    alert(goods_id)
    const token = localStorage.getItem('access_token')  //요청시 필요한 토큰 값
    const response = await fetch(`${backend_base_url}/store/goods`, {
        headers: {
            'content-type': 'application/json', "Authorization": `Bearer ${token}`,
        }, body: JSON.stringify({"goods_id": goods_id}), method: 'DELETE',
    });
    window.location.reload()
}

function deleteCard(event) {
    // 이벤트가 발생한 요소의 부모 li 요소 찾기
    let liElement = event.target.closest('li');

    // li 요소가 존재하면 제거
    if (liElement) {
        liElement.remove();
    }
}

