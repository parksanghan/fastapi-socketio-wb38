
$('#local_vid').draggable({
  containment: 'body',
  zIndex: 10000,
  // set start position at bottom right
  start: function (event, ui) {
    ui.position.left = $(window).width() - ui.helper.width();
    ui.position.top = $(window).height() - ui.helper.height();
  },
});

function checkVideoLayout() {
  const video_grid = document.getElementById("video_grid");
  const videos = video_grid.querySelectorAll("video");
  const video_count = videos.length;

  if (video_count > 0) {
    // 비디오가 있을 때만 실행됩니다.

    // 비디오 개수에 따라 동적으로 레이아웃을 조정합니다.
    for (let i = 0; i < video_count; i++) {
      if (video_count === 1) {
        videos[i].style.width = "100%";
        videos[i].style.height = "100vh";
        videos[i].style.objectFit = "cover";
      } else {
        // 2개 이상의 비디오가 있는 경우
        videos[i].style.width = "50%";
        videos[i].style.height = "50vh";
        videos[i].style.objectFit = "cover";
      }
    }
  }
} 