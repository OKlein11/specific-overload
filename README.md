# specific-overload
The repository for my blog, with much of it based off the flask tutorial blog, flaskr

### Authority
A fix to combat the flask tutorial's issue with anyone being able to make an account and post.

Every user has a certain "authority" value, basically thought of as
- 1: commenter. Cannot make posts.
- 5: Poster. can make posts, and delete and edit their own posts.
- 10: Superuser/admin. Can make posts, and delete and edit all posts. The only user with the privlege to make users with an authority greater than 1
