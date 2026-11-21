const app = Vue.createApp({
    mixins: Object.values(mixins),
    data() {
        return {
            loading: true,
            hiddenMenu: false,
            showMenuItems: false,
            menuColor: false,
            scrollTop: 0,
            renderers: [],
        };
    },
    created() {
        // 原版只监听 load 事件，但 CDN 慢的时候 Vue 执行时 load 已经过去了，
        // 监听器永远不触发 → 加载页一直转。这里补三手：
        //   1. 已经 load 完就立刻收起
        //   2. 没 load 完就监听
        //   3. 最多等 4 秒，兜底无条件收起
        if (document.readyState === "complete") {
            this.loading = false;
        } else {
            window.addEventListener("load", () => {
                this.loading = false;
            });
        }
        setTimeout(() => {
            this.loading = false;
        }, 4000);
    },
    mounted() {
        window.addEventListener("scroll", this.handleScroll, true);
        this.render();
    },
    methods: {
        render() {
            for (let i of this.renderers) i();
        },
        handleScroll() {
            let wrap = this.$refs.homePostsWrap;
            let newScrollTop = document.documentElement.scrollTop;
            if (this.scrollTop < newScrollTop) {
                this.hiddenMenu = true;
                this.showMenuItems = false;
            } else this.hiddenMenu = false;
            if (wrap) {
                if (newScrollTop <= window.innerHeight - 100) this.menuColor = true;
                else this.menuColor = false;
                if (newScrollTop <= 400) wrap.style.top = "-" + newScrollTop / 5 + "px";
                else wrap.style.top = "-80px";
            }
            this.scrollTop = newScrollTop;
        },
    },
});
app.mount("#layout");
