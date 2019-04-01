$(document).ready(function(event){  
//    Toggle for show and hide reply section for comments
    $('.reply-btn').click(function(){
        $(this).parent().next().next('.reply-section').toggle()
    });

    //  hide messages
    $(function(){
        setTimeout(function(){
            $('.alert').slideUp(2000);
        }, 5000);
    });

    //   update like section

      $(document).on('click', '#like', function(event){
        event.preventDefault();
        var pk = $(this).attr('value');
        var url = $('#likeForm').attr('action');
        csrf = $('input[name="csrfmiddlewaretoken"]').val()

        $.ajax({
            type:'POST',
            url: url,
            data: {'post_id':pk, 'csrfmiddlewaretoken': csrf },
            dataType: 'json',
            success: function(response){
                $('#like-section').html(response['form']);
            },
            error: function(rs, e){
                console.log(rs.responseText);
            }
        });
      });


    //    Update comment section
    $(document).on('submit', '.post-form', function(event){
        event.preventDefault();
        var pk = $(this).attr('value');
        console.log($(this).serialize())
        csrf = $('input[name="csrfmiddlewaretoken"]').val()
        $.ajax({
            type:'POST',
            url: $(this).attr('action'),
            data: $(this).serialize(),
            dataType: 'json',
            success: function(response){
                $('.main-comment-section').html(response['html']);
                $('textarea').val('');
                $('.reply-btn').click(function(){
                    $(this).parent().next().next('.reply-section').toggle();
                    $('textarea').val('');
                });
            },
            error: function(rs, e){
                console.log(rs.responseText);
            }
        });

    });

    //    Update Reply section
    $(document).on('submit', '.reply-form', function(event){
        event.preventDefault();
        var pk = $(this).attr('value');
        console.log($(this).serialize());
        $.ajax({
            type:'POST',
            url: $(this).attr('action'),
            data: $(this).serialize(),
            dataType: 'json',
            success: function(response){
                $('.main-comment-section').html(response['html']);
                $('textarea').val('');
                $('.reply-btn').click(function(){
                    $(this).parent().next().next('.reply-section').toggle();
                    $('textarea').val('');
                });
            },
            error: function(rs, e){
                console.log(rs.responseText);
            }
        });

    });
});