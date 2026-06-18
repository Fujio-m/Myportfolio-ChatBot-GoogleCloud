document.addEventListener("DOMContentLoaded", () => {
    /**
     * モーダル開閉の共通ヘルパー関数
     * @param {string|HTMLElement} trigger - モーダルを開くトリガー要素（ID文字列またはDOM要素）
     * @param {string} modalId - 開閉する対象モーダルのID
     * @param {Function} [onOpen] - モーダルが開く直前に実行するコールバック処理
     */
    const setupModal = (trigger, modalId, onOpen = null) => {
        const modal = document.getElementById(modalId);
        if (!modal) return;

        const triggerEl = typeof trigger === "string" ? document.getElementById(trigger) : trigger;
        if (!triggerEl) return;

        const closeBtn = modal.querySelector(".modal-close");

        const openModal = () => {
            if (onOpen) onOpen();
            modal.classList.add("active");
            document.body.style.overflow = "hidden"; // 背面のスクロールを防止
        };

        const closeModal = () => {
            modal.classList.remove("active");
            document.body.style.overflow = ""; // スクロール再有効化
        };

        triggerEl.addEventListener("click", openModal);
        if (closeBtn) closeBtn.addEventListener("click", closeModal);
        
        // モーダルの背景クリックで閉じる
        modal.addEventListener("click", (e) => {
            if (e.target === modal) closeModal();
        });
    };

    // 1. 各セクションモーダルのセットアップ
    setupModal("about-trigger", "about-modal");
    setupModal("architecture-trigger", "architecture-modal");
    setupModal("operation-trigger", "operation-modal");
    setupModal("profile-trigger", "profile-modal");

    // 2. PDCAステップ詳細モーダル（サブポップアップ）のセットアップ
    const modalTitle = document.getElementById("pdca-modal-title");
    const modalImg = document.getElementById("pdca-modal-img");
    const modalDesc = document.getElementById("pdca-modal-desc");
    const stepCards = document.querySelectorAll(".step-card-trigger");

    stepCards.forEach(card => {
        setupModal(card, "pdca-detail-modal", () => {
            const title = card.getAttribute("data-step-title");
            const imgSrc = card.getAttribute("data-step-img");
            const desc = card.getAttribute("data-step-desc");

            if (modalTitle) modalTitle.textContent = title;
            if (modalImg) {
                modalImg.src = imgSrc;
                modalImg.alt = title;
            }
            if (modalDesc) modalDesc.innerHTML = desc;
        });
    });
});
