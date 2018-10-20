class Paginator:
    def __init__(self, configuration, model, request):
        self.configuration = configuration
        self.model = model

        self.page = request.args.get('page', 1, type=int)
        self.page_size = request.args.get('page_size', configuration.per_page, type=int)

        if self.page_size > configuration.max_page_size:
            self.page_size = configuration.max_page_size

    @property
    def items(self):
        return self.model.query.paginate(self.page, self.page_size, False).items
