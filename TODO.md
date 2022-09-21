- [x] Remove `print`s and `console.log`s
- [x] Stop trying to render graphs on each page, this quick fix now makes the non-dashboard pages load slower
- [ ] Now that dashboard isnt tried to be rendered on each page, setting the theme using javascript is quite messy, use CSS @media instead
- [ ] Look into regression of andon colors updating automatically (possibly)
- [ ] A really cool plot would be a dot plot with days of the month and what color status the thing was at the end for each day, idk if 3 dot plots, I was thinking just one. Maybe each metric is:
    - status(metric): red = -1, yellow = 0, green = 1
    - overall([metrics]): round(sum(metrics)/len(metrics))
    - this might mean having redo the schema to a star schema with foreign key for each metric... ya this is a 
good excuse to refactor the database into aws mysql perhaps
