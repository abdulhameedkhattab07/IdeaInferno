// Toggle reply form visibility
function showReplyForm(commentId) {
    const replyForm = document.getElementById(`reply-form-${commentId}`);
    replyForm.classList.toggle('hidden');
}
// Submit a reply via AJAX
function submitReply(parentCommentId, postId) {
    const replyForm = document.getElementById(`reply-form-${parentCommentId}`);
    const textarea = replyForm.querySelector('textarea');
    const replyContent = textarea.value;
    // Basic AJAX request for posting reply
    fetch(`/post/${postId}/comment`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            content: replyContent,
            parent_comment_id: parentCommentId
        })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("Reply added successfully");
                // Update comment display with the new reply (or reload comments)
            }
        });
}
// Like a comment
function likeComment(commentId) {
    fetch(`/comment/${commentId}/like`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert("Liked comment!");
                // Update the like count without refreshing the page
            }
        });
}
