document.addEventListener("DOMContentLoaded", () => {
    // 1. PDCAステップ詳細モーダル制御
    const modal = document.getElementById("modal");
    const modalClose = document.getElementById("modal-close");
    const modalTitle = document.getElementById("modal-title");
    const modalImg = document.getElementById("modal-img");
    const modalDesc = document.getElementById("modal-desc");
    const stepCards = document.querySelectorAll(".step-card-trigger");

    stepCards.forEach(card => {
        card.addEventListener("click", () => {
            const title = card.getAttribute("data-step-title");
            const imgSrc = card.getAttribute("data-step-img");
            const desc = card.getAttribute("data-step-desc");

            modalTitle.textContent = title;
            modalImg.src = imgSrc;
            modalImg.alt = title;
            modalDesc.innerHTML = desc;

            modal.classList.add("active");
            document.body.style.overflow = "hidden"; // 背面のスクロールを無効化
        });
    });

    const closeModal = () => {
        modal.classList.remove("active");
        document.body.style.overflow = ""; // スクロール再有効化
    };

    if (modalClose) {
        modalClose.addEventListener("click", closeModal);
    }
    
    if (modal) {
        modal.addEventListener("click", (e) => {
            if (e.target === modal) {
                closeModal();
            }
        });
    }

    // 2. 共通モーダル開閉ロジック（ヘルパー関数）
    const setupModal = (triggerId, modalId) => {
        const trigger = document.getElementById(triggerId);
        const modal = document.getElementById(modalId);
        if (!trigger || !modal) return;

        const closeBtn = modal.querySelector(".modal-close");

        trigger.addEventListener("click", () => {
            modal.classList.add("active");
            document.body.style.overflow = "hidden";
        });

        const close = () => {
            modal.classList.remove("active");
            document.body.style.overflow = "";
        };

        if (closeBtn) closeBtn.addEventListener("click", close);
        modal.addEventListener("click", (e) => {
            if (e.target === modal) close();
        });
    };

    // 各セクションのモーダル設定
    setupModal("about-trigger", "about-modal");
    setupModal("architecture-trigger", "architecture-modal");
    setupModal("operation-trigger", "operation-modal");

    // 3. 自己紹介（Profile）モーダル制御
    const profileModal = document.getElementById("profile-modal");
    const profileTrigger = document.getElementById("profile-trigger");
    const profileModalClose = document.getElementById("profile-modal-close");

    if (profileTrigger && profileModal) {
        profileTrigger.addEventListener("click", () => {
            profileModal.classList.add("active");
            document.body.style.overflow = "hidden"; // 背面のスクロールを無効化
        });

        const closeProfileModal = () => {
            profileModal.classList.remove("active");
            document.body.style.overflow = ""; // スクロール再有効化
        };

        if (profileModalClose) {
            profileModalClose.addEventListener("click", closeProfileModal);
        }

        profileModal.addEventListener("click", (e) => {
            if (e.target === profileModal) {
                closeProfileModal();
            }
        });
    }
});
